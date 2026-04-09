"""
rutas_carrito.py
Rutas del módulo de tienda / carrito para el portal público de Concretum.
"""
import datetime
import uuid

from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user

from . import carrito_bp
from models import (
    db, Productos, CategoriasProducto, Existencias, Color,
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
def inyectar_total_carrito():
    """Expone `total_items_carrito` en todos los templates de la app."""
    total = 0
    if current_user.is_authenticated:
        carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
        if carrito:
            total = carrito.total_items
    return {'total_items_carrito': total}


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
    """
    Agrega o incrementa un producto en el carrito.
    Responde JSON para que el frontend actualice el contador sin recargar.
    Si el stock no alcanza: agrega de todas formas pero crea una solicitud de producción.
    """
    datos       = request.get_json(silent=True) or request.form
    producto_id = int(datos.get('producto_id', 0))
    cantidad    = float(datos.get('cantidad', 1))

    producto = Productos.query.filter_by(id_producto=producto_id, es_active=1).first()
    if not producto:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado.'}), 404

    existencia = Existencias.query.filter_by(producto_id=producto_id).first()
    stock_actual = float(existencia.stock_actual) if existencia else 0

    carrito = _obtener_o_crear_carrito()

    # ¿Ya está el producto en el carrito?
    item = CarritoItem.query.filter_by(
        carrito_id=carrito.id_carrito, producto_id=producto_id
    ).first()

    if item:
        item.cantidad = float(item.cantidad) + cantidad
    else:
        item = CarritoItem(
            carrito_id=carrito.id_carrito,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=producto.precio_base,
        )
        db.session.add(item)

    db.session.commit()

    # Validación de stock (solo informativa; no bloqueamos)
    advertencia = None
    if stock_actual < float(item.cantidad):
        advertencia = (
            f"El stock disponible de «{producto.nombre}» se ha agotado. "
            "Hemos enviado una solicitud para iniciar producción. "
            "Te notificaremos cuando esté listo."
        )
        _crear_notificacion(
            usuario_id=current_user.id,
            tipo='STOCK',
            titulo=f'Stock insuficiente: {producto.nombre}',
            mensaje=(
                f"Solicitaste {int(item.cantidad)} unidades de «{producto.nombre}», "
                f"pero solo hay {int(stock_actual)} en almacén. "
                "Se enviará una solicitud de producción para cubrir tu pedido."
            ),
        )
        db.session.commit()

    total_items = carrito.total_items
    subtotal    = carrito.subtotal

    return jsonify({
        'exito':       True,
        'advertencia': advertencia,
        'total_items': total_items,
        'subtotal':    f"${subtotal:,.2f}",
        'mensaje':     f'«{producto.nombre}» agregado al carrito.',
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
    """
    Procesa el formulario de pago:
    1. Crea el pedido y sus detalles.
    2. Descuenta stock de existencias.
    3. Si el stock no alcanza, crea una SolicitudProduccion y notifica al cliente.
    4. Vacía el carrito.
    5. Redirige al dashboard del cliente.
    """
    carrito = Carrito.query.filter_by(usuario_id=current_user.id).first()
    if not carrito or not carrito.items.count():
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('carrito_bp.catalogo'))

    form = CheckoutForm()
    if not form.validate_on_submit():
        flash('Por favor revisa los datos del formulario.', 'danger')
        return redirect(url_for('carrito_bp.checkout'))

    items_carrito = carrito.items.all()
    subtotal      = carrito.subtotal
    iva           = round(subtotal * 0.16, 2)
    total         = round(subtotal + iva, 2)
    folio         = _generar_folio('PED')

    # Crear pedido
    pedido = PedidoCliente(
        folio=folio,
        usuario_id=current_user.id,
        metodo_pago=form.metodo_pago.data,
        estado='PAGADO',
        subtotal=subtotal,
        iva=iva,
        total=total,
        direccion_entrega=form.direccion_entrega.data,
        notas=form.notas.data,
    )
    db.session.add(pedido)
    db.session.flush()  # Obtenemos id_pedido_cliente antes de commit

    productos_sin_stock = []

    for item in items_carrito:
        cantidad_pedida = float(item.cantidad)
        existencia      = Existencias.query.filter_by(producto_id=item.producto_id).with_for_update().first()
        stock_actual    = float(existencia.stock_actual) if existencia else 0
        stock_suficiente = 1

        # Descontar stock disponible
        if existencia:
            if stock_actual >= cantidad_pedida:
                existencia.stock_actual = stock_actual - cantidad_pedida
            else:
                # Descontamos lo que hay y marcamos insuficiente
                cantidad_faltante        = cantidad_pedida - stock_actual
                existencia.stock_actual  = 0
                stock_suficiente         = 0
                productos_sin_stock.append({
                    'producto': item.producto,
                    'faltante': cantidad_faltante,
                })

        # Detalle de pedido
        detalle = PedidoClienteDetalle(
            pedido_id=pedido.id_pedido_cliente,
            producto_id=item.producto_id,
            cantidad=cantidad_pedida,
            precio_unitario=item.precio_unitario,
            total_linea=item.subtotal,
            stock_suficiente=stock_suficiente,
        )
        db.session.add(detalle)

    # Crear solicitudes de producción para productos sin stock
    for ps in productos_sin_stock:
        solicitud = SolicitudProduccion(
            pedido_id=pedido.id_pedido_cliente,
            producto_id=ps['producto'].id_producto,
            cantidad_faltante=ps['faltante'],
        )
        db.session.add(solicitud)
        db.session.flush()

        _crear_notificacion(
            usuario_id=current_user.id,
            tipo='PRODUCCION',
            titulo=f"Producción solicitada: {ps['producto'].nombre}",
            mensaje=(
                f"No había suficiente stock para «{ps['producto'].nombre}» "
                f"(faltan {int(ps['faltante'])} unidades). "
                "Hemos enviado una solicitud de producción. "
                "Te avisaremos en cuanto sea aceptada."
            ),
            referencia_id=solicitud.id_solicitud,
            referencia_tipo='solicitud_produccion',
        )

    # Notificación de pago confirmado
    _crear_notificacion(
        usuario_id=current_user.id,
        tipo='PAGO',
        titulo=f'Pago confirmado — {folio}',
        mensaje=(
            f"Recibimos el pago de tu pedido {folio} "
            f"por un total de ${total:,.2f} MXN. "
            "Pronto recibirás más actualizaciones."
        ),
        referencia_id=pedido.id_pedido_cliente,
        referencia_tipo='pedido_cliente',
    )

    # Vaciar carrito
    for item in items_carrito:
        db.session.delete(item)

    db.session.commit()
    _registrar_auditoria_mongo('PEDIDO_CREADO', f'Pedido {folio} por ${total:,.2f}')

    flash(f'¡Pago procesado! Tu número de pedido es {folio}.', 'success')
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