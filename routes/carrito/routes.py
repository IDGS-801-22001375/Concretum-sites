"""
rutas_carrito.py
Rutas del módulo de tienda / carrito para el portal público de Concretum.
"""
import datetime
import uuid

from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from decimal import Decimal
from models import Existencias, MovimientosInventario, Venta, VentaDetalle

from . import carrito_bp
from models import (
    db, Productos, CategoriasProducto, Existencias, Color, Recetas
)
# Importar los modelos del módulo carrito
from models import (
    Carrito, CarritoItem,
    PedidoCliente, PedidoClienteDetalle,
    SolicitudProduccion, NotificacionCliente,
    Cotizacion, CotizacionDetalle,
)
from forms import AgregarAlCarritoForm, CheckoutForm, ContactoClienteForm


# ─────────────────────────────────────────────
# Utilidades internas
# ─────────────────────────────────────────────

def _obtener_o_crear_carrito():
    """Retorna el carrito activo del usuario autenticado, creándolo si no existe."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    if not carrito:
        carrito = Carrito(usuario_id=current_user.id)
        db.session.add(carrito)
        db.session.commit()
    return carrito


def _generar_folio(prefijo='PED'):
    """Genera un folio único con prefijo + fecha + fragmento UUID."""
    hoy = datetime.datetime.now().strftime('%Y%m%d')
    fragmento = str(uuid.uuid4()).replace('-', '').upper()[:6]
    return f"{prefijo}-{hoy}-{fragmento}"


def _crear_notificacion(usuario_id, tipo, titulo, mensaje,
                        referencia_id=None, referencia_tipo=None):
    """Crea una notificación para el cliente indicado."""
    notif = NotificacionCliente(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        referencia_id=referencia_id,
        referencia_tipo=referencia_tipo,
    )
    db.session.add(notif)


def _registrar_auditoria_mongo(accion, detalles):
    """Registra evento de auditoría en MongoDB (no bloqueante)."""
    try:
        from app import mongo_db
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": current_user.id if current_user.is_authenticated else None,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Carrito / Tienda",
            "user_agent": request.headers.get('User-Agent'),
            "ip": request.remote_addr,
            "fecha_creacion": datetime.datetime.utcnow(),
        })
    except Exception as error:
        print(f"Error Mongo auditoría: {error}")


# ─────────────────────────────────────────────
# CONTEXT PROCESSOR — total de ítems en carrito
# ─────────────────────────────────────────────

@carrito_bp.app_context_processor
def inyectar_carrito_global():
    """Expone el carrito completo en todos los templates del portal cliente."""
    carrito_obj = None
    items = []
    if current_user.is_authenticated:
        carrito_obj = Carrito.query.filter_by(usuario_id=current_user.id).first()
        if carrito_obj:
            items = carrito_obj.items.all()
    return {
        'carrito_global': carrito_obj,
        'items_carrito_global': items,
        'total_items_carrito': carrito_obj.total_items if carrito_obj else 0
    }

@carrito_bp.route('/mi-cuenta/datos', methods=['POST'])
@login_required
def actualizar_datos():
    from models import ClienteDetalle
    datos = request.form
    
    cliente = current_user.cliente_info
    if not cliente:
        flash('No se encontró información de cliente asociada.', 'error')
        return redirect(url_for('carrito_bp.dashboard_cliente'))

    cliente.razon_social = datos.get('razon_social', cliente.razon_social)
    cliente.rfc = datos.get('rfc', cliente.rfc)
    
    if not cliente.detalle_info:
        cliente.detalle_info = ClienteDetalle(cliente_id=cliente.id_cliente)
        db.session.add(cliente.detalle_info)
        
    cliente.detalle_info.telefono = datos.get('telefono', '')
    cliente.detalle_info.direccion = datos.get('direccion', '')
    cliente.detalle_info.ciudad = datos.get('ciudad', '')
    cliente.detalle_info.estado = datos.get('estado', '')
    cliente.detalle_info.codigo_postal = datos.get('codigo_postal', '')
    
    db.session.commit()
    flash('Tus datos han sido actualizados correctamente.', 'success')
    return redirect(url_for('carrito_bp.dashboard_cliente') + '#datos')


@carrito_bp.route('/carrito/contenido')
@login_required
def carrito_contenido():
    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    items = carrito.items.all() if carrito else []
    return render_template('tienda/_carrito_items.html', items_carrito=items, carrito=carrito)


# ─────────────────────────────────────────────
# CATÁLOGO DE PRODUCTOS (con carrito lateral)
# ─────────────────────────────────────────────

@carrito_bp.route('/productos')
def catalogo():
    """Página principal de la tienda con todos los productos y carrito lateral."""
    categoria_id = request.args.get('categoria', type=int)
    busqueda     = request.args.get('q', '').strip()

    from sqlalchemy import func

    consulta = (
        db.session.query(
            Productos,
            func.coalesce(func.sum(Existencias.stock_actual), 0).label("stock_total")
        )
        .join(CategoriasProducto, Productos.categoria_id == CategoriasProducto.id_categoria)
        .outerjoin(Existencias, Productos.id_producto == Existencias.producto_id)
        .filter(Productos.es_active == 1)
        .filter(Productos.recetas.any(Recetas.es_active == 1)) 
        .group_by(Productos.id_producto)
    )

    if categoria_id:
        consulta = consulta.filter(Productos.categoria_id == categoria_id)
    if busqueda:
        consulta = consulta.filter(
            Productos.nombre.ilike(f'%{busqueda}%') |
            Productos.descripcion.ilike(f'%{busqueda}%')
        )

    productos_lista = consulta.order_by(Productos.nombre.asc()).all()
    categorias      = CategoriasProducto.query.filter_by(es_active=1).all()

    # Carrito del usuario autenticado
    carrito      = None
    items_carrito = []
    if current_user.is_authenticated:
        carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
        if carrito:
            items_carrito = carrito.items.all()

    form_agregar = AgregarAlCarritoForm()

    return render_template(
        'tienda/catalogo.html',
        productos_lista=productos_lista,
        categorias=categorias,
        categoria_activa=categoria_id,
        busqueda=busqueda,
        items_carrito=items_carrito,
        carrito=carrito,
        form_agregar=form_agregar,
    )


# ─────────────────────────────────────────────
# AGREGAR AL CARRITO (JSON para AJAX)
# ─────────────────────────────────────────────

@carrito_bp.route('/carrito/agregar', methods=['POST'])
@login_required
def agregar_al_carrito():
    datos = request.get_json(silent=True) or request.form
    producto_id = int(datos.get('producto_id', 0))
    cantidad = Decimal(str(datos.get('cantidad', '1')))

    producto = Productos.query.filter_by(id_producto=producto_id, es_active=1).first()
    if not producto:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado.'}), 404

    existencia = Existencias.query.filter_by(producto_id=producto_id).first()
    stock_actual = float(existencia.stock_actual) if existencia else 0

    carrito = _obtener_o_crear_carrito()

    item = CarritoItem.query.filter_by(
        carrito_id=carrito.id_carrito, producto_id=producto_id
    ).first()

    if item:
        nueva_cantidad = float(item.cantidad) + float(cantidad)
        item.cantidad = nueva_cantidad
    else:
        nueva_cantidad = float(cantidad)
        item = CarritoItem(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id,
            cantidad=nueva_cantidad,
            precio_unitario=producto.precio_base,
        )
        db.session.add(item)

    db.session.commit()

    disponible = stock_actual
    solicitado = float(item.cantidad)
    faltante = max(0, solicitado - disponible)
    if faltante > 0:
        if disponible > 0:
            mensaje_stock = f"⚠️ Stock disponible: {disponible} unidades. Las {faltante} restantes se enviarán a producción tras autorizar el pedido."
        else:
            mensaje_stock = f"⚠️ Sin stock disponible. Las {solicitado} unidades se enviarán a producción tras autorizar el pedido."
    else:
        mensaje_stock = f"✅ Stock suficiente. Las {int(solicitado)} unidades están disponibles para entrega inmediata."

    total_items = carrito.total_items
    subtotal = carrito.subtotal
    item_html = render_template('tienda/_carrito_item.html', item=item)

    return jsonify({
        'exito': True,
        'mensaje_stock': mensaje_stock,
        'total_items': total_items,
        'subtotal': f"${subtotal:,.2f}",
        'subtotal_item': f"${item.subtotal:,.2f}",
        'nueva_cantidad': nueva_cantidad,
        'mensaje': f'«{producto.nombre}» agregado al carrito.',
        'item_html': item_html,
        'item_id': item.id_item
    })


# ─────────────────────────────────────────────
# QUITAR ÍTEM DEL CARRITO
# ─────────────────────────────────────────────

@carrito_bp.route('/carrito/quitar/<int:item_id>', methods=['POST'])
@login_required
def quitar_del_carrito(item_id):
    """Elimina un ítem del carrito del usuario autenticado."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    if not carrito:
        return jsonify({'exito': False, 'mensaje': 'Carrito no encontrado.'}), 404

    item = CarritoItem.query.filter_by(
        id_item=item_id, carrito_id=carrito.id_carrito
    ).first()
    if not item:
        return jsonify({'exito': False, 'mensaje': 'Ítem no encontrado.'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        'exito':       True,
        'total_items': carrito.total_items,
        'subtotal':    f"${carrito.subtotal:,.2f}",
    })


# ─────────────────────────────────────────────
# ACTUALIZAR CANTIDAD DE ÍTEM
# ─────────────────────────────────────────────

@carrito_bp.route('/carrito/actualizar/<int:item_id>', methods=['POST'])
@login_required
def actualizar_cantidad(item_id):
    """Actualiza la cantidad de un ítem en el carrito."""
    datos    = request.get_json(silent=True) or request.form
    cantidad = float(datos.get('cantidad', 1))

    if cantidad <= 0:
        return jsonify({'exito': False, 'mensaje': 'La cantidad debe ser mayor a 0.'}), 400

    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    item    = CarritoItem.query.filter_by(
        id_item=item_id, carrito_id=carrito.id_carrito
    ).first() if carrito else None

    if not item:
        return jsonify({'exito': False, 'mensaje': 'Ítem no encontrado.'}), 404

    item.cantidad = cantidad
    db.session.commit()

    existencia   = Existencias.query.filter_by(producto_id=item.producto_id).first()
    stock_actual = float(existencia.stock_actual) if existencia else 0
    advertencia  = None
    if stock_actual < cantidad:
        advertencia = f"Stock insuficiente para «{item.producto.nombre}». Se solicitará producción."

    return jsonify({
        'exito':        True,
        'advertencia':  advertencia,
        'subtotal_item': f"${item.subtotal:,.2f}",
        'total_items':  carrito.total_items,
        'subtotal':     f"${carrito.subtotal:,.2f}",
    })


# ─────────────────────────────────────────────
# CHECKOUT — GET (pasarela de pago)
# ─────────────────────────────────────────────

@carrito_bp.route('/checkout')
@login_required
def checkout():
    """Muestra el formulario de pago con el resumen del carrito."""
    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    if not carrito or not carrito.items.count():
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('carrito_bp.catalogo'))

    items_carrito = carrito.items.all()
    subtotal      = carrito.subtotal
    iva           = round(subtotal * 0.16, 2)
    total         = round(subtotal + iva, 2)
    form          = CheckoutForm()

    return render_template(
        'tienda/checkout.html',
        carrito=carrito,
        items_carrito=items_carrito,
        subtotal=subtotal,
        iva=iva,
        total=total,
        form=form,
    )


# ─────────────────────────────────────────────
# CHECKOUT — POST (procesar pago)
# ─────────────────────────────────────────────

@carrito_bp.route('/checkout', methods=['POST'])
@login_required
def procesar_pago():
    from decimal import Decimal
    
    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    if not carrito or not carrito.items.count():
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('carrito_bp.catalogo'))

    form = CheckoutForm()
    if not form.validate_on_submit():
        flash('Por favor revisa los datos del formulario.', 'danger')
        return redirect(url_for('carrito_bp.checkout'))

    items_carrito = carrito.items.all()
    subtotal = Decimal(str(carrito.subtotal))   # Convertir a Decimal de forma segura
    iva = (subtotal * Decimal('0.16')).quantize(Decimal('0.01'))  # Redondear a 2 decimales
    total = subtotal + iva
    folio = _generar_folio('PED')

    # Crear pedido en estado COTIZACION
    pedido = PedidoCliente(
        folio=folio,
        usuario_id=current_user.id,
        metodo_pago=form.metodo_pago.data,
        estado='COTIZACION',
        subtotal=subtotal,
        iva=iva,
        total=total,
        direccion_entrega=form.direccion_entrega.data,
        notas=form.notas.data,
    )
    db.session.add(pedido)
    db.session.flush()

    # Crear detalles del pedido
    for item in items_carrito:
        detalle = PedidoClienteDetalle(
            pedido_id=pedido.id_pedido_cliente,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            total_linea=item.subtotal,
            stock_suficiente=0,
            cantidad_entregada=0,
            cantidad_pendiente=item.cantidad
        )
        db.session.add(detalle)

    _crear_notificacion(
        usuario_id=current_user.id,
        tipo='INFO',
        titulo=f'Pedido solicitado - {folio}',
        mensaje=f'Tu pedido {folio} ha sido enviado para autorización. Pronto recibirás respuesta.',
        referencia_id=pedido.id_pedido_cliente,
        referencia_tipo='pedido_cliente',
    )

    # Vaciar carrito
    for item in items_carrito:
        db.session.delete(item)

    db.session.commit()
    _registrar_auditoria_mongo('PEDIDO_CREADO', f'Pedido {folio} por ${total:,.2f} (pendiente autorización)')

    flash(f'Tu pedido {folio} ha sido enviado para autorización. Te notificaremos cuando sea aprobado.', 'success')
    return redirect(url_for('carrito_bp.dashboard_cliente'))


# ─────────────────────────────────────────────
# DASHBOARD DEL CLIENTE
# ─────────────────────────────────────────────

@carrito_bp.route('/mi-cuenta')
@login_required
def dashboard_cliente():
    """Dashboard personal del cliente: historial, cotizaciones, notificaciones y configuración."""
    pedidos = (
        PedidoCliente.query
        .filter_by(usuario_id=current_user.id)
        .order_by(PedidoCliente.fecha_pedido.desc())
        .all()
    )
    cotizaciones = (
        Cotizacion.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Cotizacion.fecha_creacion.desc())
        .all()
    )
    notificaciones = (
        NotificacionCliente.query
        .filter_by(usuario_id=current_user.id)
        .order_by(NotificacionCliente.fecha_creacion.desc())
        .limit(20)
        .all()
    )
    no_leidas = NotificacionCliente.query.filter_by(
        usuario_id=current_user.id, leida=0
    ).count()

    solicitudes = (
        SolicitudProduccion.query
        .join(PedidoCliente, SolicitudProduccion.pedido_id == PedidoCliente.id_pedido_cliente)
        .filter(PedidoCliente.usuario_id == current_user.id)
        .order_by(SolicitudProduccion.fecha_solicitud.desc())
        .all()
    )

    form_contacto = ContactoClienteForm()

    return render_template(
        'tienda/dashboard_cliente.html',
        pedidos=pedidos,
        cotizaciones=cotizaciones,
        notificaciones=notificaciones,
        no_leidas=no_leidas,
        solicitudes=solicitudes,
        form_contacto=form_contacto,
    )


# ─────────────────────────────────────────────
# MARCAR NOTIFICACIÓN COMO LEÍDA
# ─────────────────────────────────────────────

@carrito_bp.route('/notificaciones/leer/<int:notif_id>', methods=['POST'])
@login_required
def marcar_leida(notif_id):
    notif = NotificacionCliente.query.filter_by(
        id_notificacion=notif_id, usuario_id=current_user.id
    ).first_or_404()
    notif.leida = 1
    db.session.commit()
    return jsonify({'exito': True})


@carrito_bp.route('/notificaciones/leer-todas', methods=['POST'])
@login_required
def marcar_todas_leidas():
    NotificacionCliente.query.filter_by(usuario_id=current_user.id, leida=0).update({'leida': 1})
    db.session.commit()
    return jsonify({'exito': True})


# ─────────────────────────────────────────────
# CONTACTO DESDE EL PORTAL
# ─────────────────────────────────────────────

@carrito_bp.route('/mi-cuenta/contacto', methods=['POST'])
@login_required
def enviar_contacto():
    """Guarda el mensaje de contacto del cliente (registro en Mongo)."""
    form = ContactoClienteForm()
    if form.validate_on_submit():
        try:
            from app import mongo_db
            mongo_db.mensajes_contacto.insert_one({
                "usuario_id": current_user.id,
                "email":      current_user.email,
                "asunto":     form.asunto.data,
                "mensaje":    form.mensaje.data,
                "fecha":      datetime.datetime.utcnow(),
            })
            flash('Tu mensaje fue enviado. Te responderemos pronto.', 'success')
        except Exception as error:
            flash('Ocurrió un error al enviar el mensaje. Intenta de nuevo.', 'danger')
    else:
        flash('Por favor completa todos los campos requeridos.', 'danger')
    return redirect(url_for('carrito_bp.dashboard_cliente') + '#contacto')


@carrito_bp.route('/pedido/<int:pedido_id>')
@login_required
def ver_pedido_cliente(pedido_id):
    pedido = PedidoCliente.query.filter_by(id_pedido_cliente=pedido_id, usuario_id=current_user.id).first_or_404()
    return render_template('tienda/pedido_detalle_cliente.html', pedido=pedido)

@carrito_bp.route('/notificaciones/no-leidas')
@login_required
def notificaciones_no_leidas():
    count = NotificacionCliente.query.filter_by(usuario_id=current_user.id, leida=0).count()
    return jsonify({'count': count})


@carrito_bp.route('/pedido/<int:pedido_id>/responder_fecha', methods=['POST'])
@login_required
def responder_fecha_pedido(pedido_id):
    from routes.comercial.routes import calcular_costo_unitario_producto
    pedido = PedidoCliente.query.filter_by(id_pedido_cliente=pedido_id, usuario_id=current_user.id).first_or_404()
    
    if pedido.estado != 'NEGOCIANDO_FECHA':
        flash('Este pedido no está pendiente de tu respuesta.', 'warning')
        return redirect(url_for('carrito_bp.ver_pedido_cliente', pedido_id=pedido_id))

    accion = request.form.get('accion')

    if accion == 'rechazar':
        pedido.estado = 'RECHAZADO'
        db.session.commit()
        flash('Has rechazado la fecha propuesta. El pedido ha sido cancelado.', 'info')
        return redirect(url_for('carrito_bp.ver_pedido_cliente', pedido_id=pedido_id))
    
    elif accion == 'aceptar':
        try:
            from models import Cliente
            cliente = Cliente.query.filter_by(usuario_id=pedido.usuario_id).first()
            if not cliente:
                cliente = Cliente(
                    usuario_id=pedido.usuario_id,
                    razon_social=pedido.usuario.username,
                    email=pedido.usuario.email,
                    es_activo=1
                )
                db.session.add(cliente)
                db.session.flush()         
            cliente_id = cliente.id_cliente

            productos_sin_stock = []
            total_venta = Decimal('0.00')

            for detalle in pedido.detalles:
                existencia = Existencias.query.filter_by(producto_id=detalle.producto.id).first()
                stock_actual = Decimal(str(existencia.stock_actual)) if existencia else Decimal('0')
                entregable = min(Decimal(str(detalle.cantidad)), stock_actual)
                if entregable > 0:
                    total_venta += entregable * Decimal(str(detalle.precio_unitario))

            venta = None
            if total_venta > 0:
                folio_venta = f'VTA-{pedido.folio}'
                subtotal_venta = total_venta / Decimal('1.16')
                iva_venta = total_venta - subtotal_venta

                venta = Venta(
                    folio=folio_venta,
                    cliente_id=cliente_id,
                    usuario_id=None, # Venta automatizada
                    metodo_pago=pedido.metodo_pago,
                    estado='COBRADO' if pedido.metodo_pago != 'CREDITO' else 'CREDITO',
                    subtotal=subtotal_venta,
                    iva=iva_venta,
                    total=total_venta,
                    fecha_venta=datetime.datetime.now()
                )
                db.session.add(venta)
                db.session.flush()

            for detalle in pedido.detalles:
                producto = detalle.producto
                cantidad_pedida = Decimal(str(detalle.cantidad))
                existencia = Existencias.query.filter_by(producto_id=producto.id).first()
                stock_actual = Decimal(str(existencia.stock_actual)) if existencia else Decimal('0')

                entregable = min(cantidad_pedida, stock_actual)
                faltante = cantidad_pedida - entregable

                if entregable > 0:
                    existencia.stock_actual = float(stock_actual - entregable)
                    movimiento = MovimientosInventario(
                        existencia_id=existencia.id_existencias,
                        usuario_id=None,
                        tipo='SALIDA',
                        cantidad=entregable,
                        motivo=f'Venta auto-aceptada pedido {pedido.folio}'
                    )
                    db.session.add(movimiento)

                    if venta:
                        costo_unit = calcular_costo_unitario_producto(producto.id)
                        detalle_venta = VentaDetalle(
                            venta_id=venta.id_venta,
                            producto_id=producto.id,
                            cantidad=entregable,
                            costo_unitario=costo_unit, 
                            precio_unitario=detalle.precio_unitario,
                            total_linea=entregable * Decimal(str(detalle.precio_unitario))
                        )
                        db.session.add(detalle_venta)

                detalle.cantidad_entregada = int(entregable)
                detalle.cantidad_pendiente = int(faltante)

                if faltante > 0:
                    solicitud = SolicitudProduccion(
                        pedido_id=pedido.id_pedido_cliente,
                        producto_id=producto.id,
                        cantidad_faltante=faltante,
                        estado='PENDIENTE'
                    )
                    db.session.add(solicitud)

            if all(d.cantidad_pendiente == 0 for d in pedido.detalles):
                pedido.estado = 'ENTREGADO'
            elif any(d.cantidad_pendiente > 0 for d in pedido.detalles) and any(d.cantidad_entregada > 0 for d in pedido.detalles):
                pedido.estado = 'PARCIALMENTE_ENTREGADO'
            else:
                pedido.estado = 'EN_PRODUCCION'

            pedido.fecha_autorizacion = datetime.datetime.now()
            db.session.commit()

            flash('¡Excelente! Has aceptado la fecha y tu pedido se ha autorizado automáticamente.', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al procesar tu autorización: {str(e)}', 'danger')

    return redirect(url_for('carrito_bp.ver_pedido_cliente', pedido_id=pedido_id))