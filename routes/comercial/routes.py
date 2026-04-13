from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from datetime import datetime, date, time as dt_time
from decimal import Decimal
from sqlalchemy import func, or_, desc, asc
from flask_security import login_required, roles_accepted, current_user

from models import (
    db, Venta, VentaDetalle, CorteCaja, CorteDesglose, Cliente,
    Productos, Existencias, MovimientosInventario, User, CategoriasProducto,
    PedidoCliente, PedidoClienteDetalle, SolicitudProduccion, NotificacionCliente, Recetas
)
from forms import VentaForm, CorteForm
from routes.comercial import comercial_bp
from routes.carrito.routes import _crear_notificacion
import threading
from copy import copy

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def _guardar_en_mongo(datos_auditoria):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one(datos_auditoria)
    except Exception as e:
        print(f"Error Mongo (Async): {e}")

def registrar_auditoria(usuario_accion, accion, detalles):
    user_agent = request.headers.get('User-Agent') if request else 'Desconocido'
    ip_addr = request.remote_addr if request else '0.0.0.0'
    
    datos_auditoria = {
        "usuario_id": usuario_accion,
        "evento": accion,
        "detalles": detalles,
        "modulo": "Comercial", 
        "user_agent": user_agent,
        "ip": ip_addr,
        "fecha_creacion": datetime.utcnow() # <--- CORRECCIÓN AQUÍ
    }
    
    threading.Thread(target=_guardar_en_mongo, args=(datos_auditoria,)).start()

def calcular_costo_unitario_producto(producto_id):
    producto = Productos.query.get(producto_id)
    receta = next((r for r in producto.recetas if r.es_active == 1), None)
    if receta and receta.cuanto_produce > 0:
        costo_receta = Decimal('0.00')
        for ing in receta.detalles:
            mp = ing.materia_prima
            if mp and mp.costo_unitario:
                costo_receta += Decimal(str(ing.cantidad)) * Decimal(str(mp.costo_unitario))
        return costo_receta / Decimal(str(receta.cuanto_produce))
    return Decimal(str(producto.precio_base)) * Decimal('0.60') 

# ============================================================
# DASHBOARD
# ============================================================

@comercial_bp.route('/dashboard')
@login_required
def dashboard():
    hoy = date.today()
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        if start_date_str and end_date_str:
            fecha_inicio = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if fecha_inicio == fecha_fin:
                texto_fecha = fecha_inicio.strftime('%d/%m/%Y')
            else:
                texto_fecha = f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        else:
            fecha_inicio = hoy
            fecha_fin = hoy
            texto_fecha = hoy.strftime('%d/%m/%Y')
            
    except ValueError:
        fecha_inicio = hoy
        fecha_fin = hoy
        texto_fecha = hoy.strftime('%d/%m/%Y')

    inicio_rango = datetime.combine(fecha_inicio, dt_time.min)
    fin_rango    = datetime.combine(fecha_fin, dt_time.max)

    ventas_hoy = Venta.query.filter(
        Venta.fecha_venta >= inicio_rango,
        Venta.fecha_venta <= fin_rango
    ).all()

    ventas_dia      = sum(float(v.total) for v in ventas_hoy)
    num_ventas      = len(ventas_hoy)
    ticket_promedio = round(ventas_dia / num_ventas, 2) if num_ventas > 0 else 0

    ids_ventas_hoy = [v.id_venta for v in ventas_hoy]

    costo_total = Decimal('0.00')

    if ids_ventas_hoy:
        detalles_hoy = VentaDetalle.query.filter(
            VentaDetalle.venta_id.in_(ids_ventas_hoy)
        ).all()

        for det in detalles_hoy:
            if det.costo_unitario and det.costo_unitario > 0:
                costo_total += Decimal(str(det.costo_unitario)) * Decimal(str(det.cantidad))
            else:
                costo_total += calcular_costo_unitario_producto(det.producto_id) * Decimal(str(det.cantidad))

    utilidad_dia = float(Decimal(str(ventas_dia)) - costo_total)

    productos_top = db.session.query(
        Productos.nombre,
        CategoriasProducto.nombre.label('categoria'),
        func.sum(VentaDetalle.cantidad).label('cantidad'),
        func.sum(VentaDetalle.total_linea).label('total')
    ).join(VentaDetalle, VentaDetalle.producto_id == Productos.id_producto)\
    .join(CategoriasProducto, Productos.categoria_id == CategoriasProducto.id_categoria)\
    .join(Venta, Venta.id_venta == VentaDetalle.venta_id)\
    .filter(
        Venta.fecha_venta >= inicio_rango,
        Venta.fecha_venta <= fin_rango
    )\
    .group_by(Productos.id_producto, Productos.nombre, CategoriasProducto.nombre)\
    .order_by(func.sum(VentaDetalle.cantidad).desc())\
    .limit(5).all()

    categorias_top = db.session.query(
        CategoriasProducto.nombre,
        func.sum(VentaDetalle.cantidad).label('cantidad')
    ).join(Productos, Productos.categoria_id == CategoriasProducto.id_categoria)\
    .join(VentaDetalle, VentaDetalle.producto_id == Productos.id_producto)\
    .join(Venta, Venta.id_venta == VentaDetalle.venta_id)\
    .filter(
        Venta.fecha_venta >= inicio_rango,
        Venta.fecha_venta <= fin_rango
    )\
    .group_by(CategoriasProducto.nombre)\
    .order_by(func.sum(VentaDetalle.cantidad).desc())\
    .limit(4).all()

    total_unidades = sum(c.cantidad for c in categorias_top) if categorias_top else 1
    presentaciones_top = [{
        'nombre': c.nombre,
        'cantidad': int(c.cantidad),
        'porcentaje': round((c.cantidad / total_unidades) * 100)
    } for c in categorias_top]

    ventas_recientes_q = Venta.query.filter(
        Venta.fecha_venta >= inicio_rango,
        Venta.fecha_venta <= fin_rango
    ).order_by(Venta.fecha_creacion.desc()).limit(10).all()
    
    ventas_recientes = [{
        'folio': v.folio,
        'cliente': v.cliente.razon_social if v.cliente else 'Público General',
        'total': f'{v.total:,.2f}',
        'metodo_pago': v.metodo_pago.capitalize(),
        'hora': v.fecha_venta.strftime('%H:%M'),
        'estado': v.estado.capitalize()
    } for v in ventas_recientes_q]

    return render_template('comercial/dashboard.html',
        fecha_hoy        = texto_fecha, 
        ventas_dia       = f'{ventas_dia:,.2f}',
        num_ventas       = num_ventas,
        ticket_promedio  = f'{ticket_promedio:,.2f}',
        utilidad_dia     = f'{utilidad_dia:,.2f}',
        productos_top    = productos_top,
        presentaciones_top = presentaciones_top,
        ventas_recientes = ventas_recientes,
    )

# ============================================================
# VENTAS (STANDARIZADO)
# ============================================================

@comercial_bp.route('/ventas')
@login_required
def ventas():
    form     = VentaForm()
    clientes = Cliente.query.filter_by(es_activo=1).order_by(Cliente.razon_social).all()
    prods = Productos.query.filter(
        Productos.es_active == 1,
        Productos.recetas.any(Recetas.es_active == 1)
    ).order_by(Productos.nombre).all()

    form.cliente_id.choices = [(c.id_cliente, c.razon_social) for c in clientes]

    # Calcular KPIs del mes
    hoy_ventas  = datetime.now()
    inicio_mes = datetime(hoy_ventas.year, hoy_ventas.month, 1)
    if hoy_ventas.month == 12:
        fin_mes = datetime(hoy_ventas.year + 1, 1, 1)
    else:
        fin_mes = datetime(hoy_ventas.year, hoy_ventas.month + 1, 1)

    ventas_mes_q = Venta.query.filter(
        Venta.fecha_venta >= inicio_mes,
        Venta.fecha_venta <  fin_mes
    ).all()

    ventas_mes      = sum(float(v.total) for v in ventas_mes_q)
    num_ventas      = len(ventas_mes_q)
    ticket_promedio = round(ventas_mes / num_ventas, 2) if num_ventas > 0 else 0
    cuentas_cobrar  = sum(float(v.total) for v in ventas_mes_q if v.estado == 'CREDITO')

    return render_template('comercial/ventas.html',
        form               = form,
        clientes           = clientes,
        productos          = prods,
        ventas_mes         = f'{ventas_mes:,.2f}',
        num_ventas         = num_ventas,
        ticket_promedio    = f'{ticket_promedio:,.2f}',
        cuentas_por_cobrar = f'{cuentas_cobrar:,.2f}',
    )

@comercial_bp.route('/ventas/api', methods=['GET'])
@login_required
def api_ventas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'fecha_creacion')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = Venta.query
    if search:
        query = query.filter(or_(
            Venta.folio.ilike(f'%{search}%'),
            Venta.cliente.has(Cliente.razon_social.ilike(f'%{search}%'))
        ))
    
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Venta, sort_by, Venta.fecha_creacion)))
    else:
        query = query.order_by(desc(getattr(Venta, sort_by, Venta.fecha_creacion)))
        
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = []
    for v in paginated.items:
        items.append({
            'id': v.id_venta,
            'folio': v.folio,
            'cliente': v.cliente.razon_social if v.cliente else 'Público General',
            'num_productos': int(sum(d.cantidad for d in v.detalle)),
            'total': float(v.total),
            'metodo_pago': v.metodo_pago,
            'fecha': v.fecha_venta.strftime('%d/%m/%Y'),
            'estado': v.estado
        })
        
    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@comercial_bp.route('/ventas/nueva', methods=['POST'])
@login_required
def nueva_venta():
    cliente_id   = request.form.get('cliente_id', type=int)
    metodo_pago  = request.form.get('metodo_pago')
    fecha_str    = request.form.get('fecha')
    producto_ids = request.form.getlist('producto_id[]')
    cantidades   = request.form.getlist('cantidad[]')
    precios      = request.form.getlist('precio[]')

    if not cliente_id or not metodo_pago or not producto_ids:
        return jsonify({'success': False, 'message': 'Completa todos los campos requeridos.'}), 400

    try:
        fecha_venta = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.now()
        folio = 'TEMP'
        subtotal      = Decimal('0.00')
        detalle_items = []

        for pid, cant_str, precio_str in zip(producto_ids, cantidades, precios):
            if not pid or not cant_str or not precio_str:
                continue

            try:
                cant = Decimal(str(cant_str).strip())
                if cant <= 0:
                    raise Exception(f"La cantidad debe ser mayor a 0.")
            except Exception as e:
                return jsonify({'success': False, 'message': f"Cantidad inválida '{cant_str}': {str(e)}"}), 400

            try:
                precio = Decimal(str(precio_str).strip())
                if precio < 0:
                    raise Exception(f"El precio no puede ser negativo.")
            except Exception as e:
                return jsonify({'success': False, 'message': f"Precio inválido '{precio_str}': {str(e)}"}), 400

            total_linea = cant * precio
            subtotal += total_linea

            producto_obj = Productos.query.get(int(pid))
            nombre_producto = producto_obj.nombre if producto_obj else f"ID {pid}"

            existencia = Existencias.query.with_for_update().filter_by(producto_id=int(pid)).first()
            if not existencia:
                return jsonify({'success': False, 'message': f"El producto '{nombre_producto}' no tiene registro de inventario."}), 400
            if existencia.stock_actual < cant:
                return jsonify({'success': False, 'message': f"Stock insuficiente para '{nombre_producto}': disponible {float(existencia.stock_actual):.3f}, solicitado {float(cant):.3f}."}), 400

            existencia.stock_actual -= cant

            mov = MovimientosInventario(
                existencia_id=existencia.id_existencias,
                usuario_id=current_user.id,
                tipo='SALIDA',
                cantidad=cant,
                motivo=f'Venta Comercial Folio: {folio}'
            )
            db.session.add(mov)
            detalle_items.append((int(pid), cant, precio, total_linea))

        iva    = subtotal * Decimal('0.16')
        total  = subtotal + iva
        estado = 'CREDITO' if metodo_pago == 'CREDITO' else 'COBRADO'

        venta = Venta(
            folio       = folio,
            cliente_id  = cliente_id,
            usuario_id  = current_user.id,
            metodo_pago = metodo_pago.upper(),
            estado      = estado,
            subtotal    = subtotal,
            iva         = iva,
            total       = total,
            fecha_venta = fecha_venta,
        )
        db.session.add(venta)
        db.session.flush()

        # Actualizar el folio real
        venta.folio = f'V-{datetime.now().year}-{str(venta.id_venta).zfill(5)}'
        
        # Actualizar motivo de movimiento con el folio real
        for mov in db.session.new:
            if isinstance(mov, MovimientosInventario) and mov.motivo == 'Venta Comercial Folio: TEMP':
                mov.motivo = f'Venta Comercial Folio: {venta.folio}'

        for pid, cant, precio, total_linea in detalle_items:
            costo_unit = calcular_costo_unitario_producto(int(pid)) 
            
            det = VentaDetalle(
                venta_id        = venta.id_venta,
                producto_id     = pid,
                cantidad        = cant,
                costo_unitario  = costo_unit, 
                precio_unitario = precio,
                total_linea     = total_linea,
            )
            db.session.add(det)

        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Venta", f"Venta registrada: {venta.folio} por ${total:,.2f}")
        
        # Retornamos JSON indicando éxito
        return jsonify({'success': True, 'message': f'Venta {venta.folio} registrada correctamente.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al registrar la venta: {str(e)}'}), 500

# ============================================================
# TICKET
# ============================================================

@comercial_bp.route('/ticket', methods=['GET'])
@login_required
def ticket():
    roles_usuario = [r.name for r in current_user.roles]
    puede_ver_todas = any(r in roles_usuario for r in ['ADMINISTRADOR', 'GERENTE_VENTAS', 'ADMIN'])

    if puede_ver_todas:
        lista_ventas = Venta.query.order_by(Venta.fecha_creacion.desc()).all()
    else:
        lista_ventas = Venta.query.filter_by(
            usuario_id=current_user.id
        ).order_by(Venta.fecha_creacion.desc()).all()

    venta_id = request.args.get('venta_id', type=int)
    venta    = None

    if venta_id:
        venta = Venta.query.get(venta_id)

        if venta and not puede_ver_todas:
            if venta.usuario_id != current_user.id:
                flash('No tienes permiso para ver este ticket.', 'danger')
                return redirect(url_for('comercial_bp.ticket'))

    return render_template('comercial/ticket.html',
        ventas = lista_ventas,
        venta  = venta,
    )

# ============================================================
# CORTE DE CAJA
# ============================================================

@comercial_bp.route('/corte')
@login_required
def corte():
    form = CorteForm()
    hoy  = date.today()

    inicio_hoy = datetime.combine(hoy, dt_time.min)
    fin_hoy    = datetime.combine(hoy, dt_time.max)

    corte_activo = CorteCaja.query.filter(
        CorteCaja.periodo_inicio >= inicio_hoy,
        CorteCaja.periodo_inicio <= fin_hoy,
        CorteCaja.estado == 'ABIERTO'
    ).first()

    ventas_hoy = Venta.query.filter(
        Venta.fecha_venta >= inicio_hoy,
        Venta.fecha_venta <= fin_hoy
    ).all()

    total_ventas   = sum(float(v.total) for v in ventas_hoy)
    total_cobrado  = sum(float(v.total) for v in ventas_hoy if v.estado == 'COBRADO')
    ventas_credito = sum(float(v.total) for v in ventas_hoy if v.estado == 'CREDITO')

    desglose_pago = []
    for forma in ['EFECTIVO', 'TRANSFERENCIA', 'CHEQUE', 'CREDITO']:
        vs = [v for v in ventas_hoy if v.metodo_pago == forma]
        if vs:
            desglose_pago.append({
                'forma'      : forma.capitalize(),
                'operaciones': len(vs),
                'monto'      : f'{sum(float(v.total) for v in vs):,.2f}',
                'es_credito' : forma == 'CREDITO',
            })

    historial_cortes_q = CorteCaja.query.filter(CorteCaja.estado == 'CERRADO').order_by(CorteCaja.fecha_creacion.desc()).limit(10).all()
    
    historial_cortes = [{
        'fecha': c.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        'cajero': User.query.get(c.usuario_id).username if c.usuario_id else 'Sistema',
        'total_ventas': f'{c.total_ventas:,.2f}',
        'total_cobrado': f'{c.total_cobrado:,.2f}',
        'utilidad': f'{c.utilidad:,.2f}'
    } for c in historial_cortes_q]

    return render_template('comercial/corte.html',
        form               = form,
        periodo            = f'Hoy {hoy.strftime("%d/%m/%Y")}',
        cajero             = current_user.username,
        fondo_inicial      = f'{float(corte_activo.fondo_inicial):,.2f}' if corte_activo else '0.00',
        total_ventas       = f'{total_ventas:,.2f}',
        total_cobrado      = f'{total_cobrado:,.2f}',
        ventas_credito     = f'{ventas_credito:,.2f}',
        devoluciones       = '0.00',
        salida_proveedores = '0.00',
        desglose_pago      = desglose_pago,
        historial_cortes   = historial_cortes,
    )

@comercial_bp.route('/corte/realizar', methods=['POST'])
@login_required
def realizar_corte():
    fondo_inicial = request.form.get('fondo_inicial', 0, type=float)
    hoy           = date.today()

    inicio_hoy = datetime.combine(hoy, dt_time.min)
    fin_hoy    = datetime.combine(hoy, dt_time.max)

    corte_existente = CorteCaja.query.filter(
        CorteCaja.periodo_inicio >= inicio_hoy,
        CorteCaja.periodo_inicio <= fin_hoy
    ).first()

    if corte_existente:
        if corte_existente.estado == 'ABIERTO':
            flash('Ya tienes un corte abierto para hoy. Ciérralo antes de iniciar uno nuevo.', 'warning')
        else:
            # Si ya está CERRADO, bloqueamos que hagan otro corte hoy
            flash('Ya realizaste y cerraste el corte de caja de hoy.', 'error')
        return redirect(url_for('comercial_bp.corte'))

    ventas_hoy = Venta.query.filter(
        Venta.fecha_venta >= inicio_hoy,
        Venta.fecha_venta <= fin_hoy
    ).all()
    total_ventas   = sum(float(v.total) for v in ventas_hoy)
    total_cobrado  = sum(float(v.total) for v in ventas_hoy if v.estado == 'COBRADO')
    ventas_credito = sum(float(v.total) for v in ventas_hoy if v.estado == 'CREDITO')
    costo_total_corte = Decimal('0.00')
    ids_ventas_corte = [v.id_venta for v in ventas_hoy]
    
    if ids_ventas_corte:
        detalles_corte = VentaDetalle.query.filter(VentaDetalle.venta_id.in_(ids_ventas_corte)).all()
        for det in detalles_corte:
            if det.costo_unitario and det.costo_unitario > 0:
                costo_total_corte += Decimal(str(det.costo_unitario)) * Decimal(str(det.cantidad))
            else:
                costo_total_corte += calcular_costo_unitario_producto(det.producto_id) * Decimal(str(det.cantidad))

    # La utilidad real es el total de la venta menos el costo de producción
    utilidad = float(Decimal(str(total_ventas)) - costo_total_corte)

    try:
        nuevo_corte = CorteCaja(
            usuario_id     = current_user.id,
            periodo_inicio = datetime.combine(hoy, dt_time.min),
            fondo_inicial  = fondo_inicial,
            total_ventas   = total_ventas,
            total_cobrado  = total_cobrado,
            ventas_credito = ventas_credito,
            utilidad       = utilidad,
            estado         = 'ABIERTO',
        )
        db.session.add(nuevo_corte)
        db.session.flush()

        for forma in ['EFECTIVO', 'TRANSFERENCIA', 'CHEQUE', 'CREDITO']:
            vs = [v for v in ventas_hoy if v.metodo_pago == forma]
            if vs:
                desglose = CorteDesglose(
                    corte_id    = nuevo_corte.id_corte,
                    forma_pago  = forma,
                    operaciones = len(vs),
                    monto       = sum(float(v.total) for v in vs),
                    es_credito  = forma == 'CREDITO',
                )
                db.session.add(desglose)

        db.session.commit()
        registrar_auditoria(current_user.id, "Apertura Corte", f"Corte iniciado. Fondo inicial: ${fondo_inicial:,.2f}")
        flash('Corte iniciado correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al realizar el corte: {str(e)}', 'danger')

    return redirect(url_for('comercial_bp.corte'))


@comercial_bp.route('/corte/cerrar', methods=['POST'])
@login_required
def cerrar_corte():
    hoy = date.today()
    inicio_hoy = datetime.combine(hoy, dt_time.min)
    fin_hoy    = datetime.combine(hoy, dt_time.max)

    corte_activo = CorteCaja.query.filter(
        CorteCaja.periodo_inicio >= inicio_hoy,
        CorteCaja.periodo_inicio <= fin_hoy,
        CorteCaja.estado == 'ABIERTO'
    ).first()

    if corte_activo:
        try:
            corte_activo.estado      = 'CERRADO'
            corte_activo.periodo_fin = datetime.now()
            db.session.commit()
            
            registrar_auditoria(current_user.id, "Cierre Corte", f"Corte cerrado. Ventas Totales: ${corte_activo.total_ventas:,.2f}")
            flash('Corte cerrado correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al cerrar el corte: {str(e)}', 'danger')
    else:
        flash('No hay corte activo para cerrar.', 'warning')

    return redirect(url_for('comercial_bp.corte'))

# ============================================================
# PEDIDOS PENDIENTES
# ============================================================

@comercial_bp.route('/pedidos/pendientes')
@login_required
@roles_accepted('ADMINISTRADOR', 'VENTAS')
def pedidos_pendientes():
    pedidos = PedidoCliente.query.filter(
        PedidoCliente.estado.in_(['COTIZACION', 'NEGOCIANDO_FECHA'])
    ).order_by(PedidoCliente.fecha_pedido.desc()).all()
    
    return render_template('comercial/pedidos_pendientes.html', pedidos=pedidos)

@comercial_bp.route('/pedidos/<int:pedido_id>')
@login_required
@roles_accepted('ADMINISTRADOR', 'VENTAS')
def ver_pedido(pedido_id):
    pedido = PedidoCliente.query.get_or_404(pedido_id)
    return render_template('comercial/pedido_detalle.html', pedido=pedido)

@comercial_bp.route('/pedidos/<int:pedido_id>/autorizar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'VENTAS')
def autorizar_pedido(pedido_id):
    from decimal import Decimal

    pedido = PedidoCliente.query.get_or_404(pedido_id)
    if pedido.estado != 'COTIZACION':
        flash('Este pedido ya no está pendiente de autorización.', 'warning')
        return redirect(url_for('comercial_bp.pedidos_pendientes'))

    try:
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

        detalles = pedido.detalles
        productos_sin_stock = []

        total_venta = Decimal('0.00')
        for detalle in detalles:
            producto = detalle.producto
            cantidad_pedida = Decimal(str(detalle.cantidad))
            existencia = Existencias.query.filter_by(producto_id=producto.id).first()
            stock_actual = Decimal(str(existencia.stock_actual)) if existencia else Decimal('0')
            entregable = min(cantidad_pedida, stock_actual)
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
                usuario_id=current_user.id,
                metodo_pago=pedido.metodo_pago,
                estado='COBRADO' if pedido.metodo_pago != 'CREDITO' else 'CREDITO',
                subtotal=subtotal_venta,
                iva=iva_venta,
                total=total_venta,
                fecha_venta=datetime.now()
            )
            db.session.add(venta)
            db.session.flush()

        for detalle in detalles:
            producto = detalle.producto
            cantidad_pedida = Decimal(str(detalle.cantidad))
            existencia = Existencias.query.filter_by(producto_id=producto.id).first()
            stock_actual = Decimal(str(existencia.stock_actual)) if existencia else Decimal('0')

            entregable = min(cantidad_pedida, stock_actual)
            faltante = cantidad_pedida - entregable

            if entregable > 0:
                existencia.stock_actual = stock_actual - entregable

                movimiento = MovimientosInventario(
                    existencia_id=existencia.id_existencias,
                    usuario_id=current_user.id,
                    tipo='SALIDA',
                    cantidad=entregable,
                    motivo=f'Venta por pedido {pedido.folio}'
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

                detalle.cantidad_entregada = entregable
                detalle.cantidad_pendiente = faltante
            else:
                detalle.cantidad_entregada = Decimal('0')
                detalle.cantidad_pendiente = cantidad_pedida

            if faltante > 0:
                solicitud = SolicitudProduccion(
                    pedido_id=pedido.id_pedido_cliente,
                    producto_id=producto.id,
                    cantidad_faltante=faltante,
                    estado='PENDIENTE'
                )
                db.session.add(solicitud)
                productos_sin_stock.append((producto.nombre, faltante))

        if all(d.cantidad_pendiente == 0 for d in detalles):
            pedido.estado = 'ENTREGADO'
        elif any(d.cantidad_pendiente > 0 for d in detalles) and any(d.cantidad_entregada > 0 for d in detalles):
            pedido.estado = 'PARCIALMENTE_ENTREGADO'
        else:
            pedido.estado = 'EN_PRODUCCION'

        pedido.fecha_autorizacion = datetime.now()
        db.session.commit()

        mensaje = f"Tu pedido {pedido.folio} ha sido autorizado. "
        if total_venta > 0:
            mensaje += f"Se entregarán {int(total_venta)} unidades de inmediato. "
        if productos_sin_stock:
            mensaje += "Los siguientes productos están pendientes de producción: " + \
                       ", ".join([f"{p[0]} ({int(p[1])} u)" for p in productos_sin_stock])
        else:
            mensaje += "Todo el pedido está listo para entrega."

        _crear_notificacion(
            usuario_id=pedido.usuario_id,
            tipo='INFO',
            titulo=f'Pedido autorizado - {pedido.folio}',
            mensaje=mensaje,
            referencia_id=pedido.id_pedido_cliente,
            referencia_tipo='pedido_cliente',
        )

        flash(f'Pedido {pedido.folio} autorizado correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al autorizar el pedido: {str(e)}', 'danger')
        current_app.logger.error(f"Error autorizando pedido {pedido_id}: {e}")

    return redirect(url_for('comercial_bp.pedidos_pendientes'))


@comercial_bp.route('/pedidos/<int:pedido_id>/proponer_fecha', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'VENTAS')
def proponer_fecha_pedido(pedido_id):
    pedido = PedidoCliente.query.get_or_404(pedido_id)
    if pedido.estado != 'COTIZACION':
        flash('Este pedido ya no está en fase de cotización.', 'warning')
        return redirect(url_for('comercial_bp.pedidos_pendientes'))

    fecha_propuesta = request.form.get('fecha_propuesta')
    motivo = request.form.get('motivo', 'Ajuste por tiempos de producción')

    if not fecha_propuesta:
        flash('Debes seleccionar una fecha.', 'danger')
        return redirect(url_for('comercial_bp.ver_pedido', pedido_id=pedido.id_pedido_cliente))

    # Actualizar estado y fecha
    pedido.estado = 'NEGOCIANDO_FECHA'
    pedido.fecha_propuesta_entrega = datetime.strptime(fecha_propuesta, '%Y-%m-%d').date()
    pedido.motivo_rechazo = motivo 

    _crear_notificacion(
        usuario_id=pedido.usuario_id,
        tipo='INFO',
        titulo=f'Propuesta de fecha - Pedido {pedido.folio}',
        mensaje=f'Tenemos una propuesta de fecha de entrega para tu pedido ({fecha_propuesta}). Por favor, revisa tu panel para aceptarla.',
        referencia_id=pedido.id_pedido_cliente,
        referencia_tipo='pedido_cliente',
    )

    db.session.commit()

    flash(f'Propuesta enviada al cliente para el pedido {pedido.folio}.', 'info')
    return redirect(url_for('comercial_bp.pedidos_pendientes'))