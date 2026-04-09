from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, time as dt_time
from decimal import Decimal
from sqlalchemy import func
from flask_security import login_required, roles_accepted, current_user

from models import db, Venta, VentaDetalle, CorteCaja, CorteDesglose, Cliente, Productos, Existencias, MovimientosInventario, User, CategoriasProducto
from forms import VentaForm, CorteForm
from routes.comercial import comercial_bp

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Comercial",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

# ============================================================
# DASHBOARD
# ============================================================

@comercial_bp.route('/dashboard')
@login_required
def dashboard():
    hoy = date.today()

    inicio_hoy = datetime.combine(hoy, dt_time.min)
    fin_hoy    = datetime.combine(hoy, dt_time.max)
    ventas_hoy = Venta.query.filter(
        Venta.fecha_venta >= inicio_hoy,
        Venta.fecha_venta <= fin_hoy
    ).all()

    ventas_dia      = sum(float(v.total) for v in ventas_hoy)
    num_ventas      = len(ventas_hoy)
    ticket_promedio = round(ventas_dia / num_ventas, 2) if num_ventas > 0 else 0

    from models import VentaDetalle, Productos

    ids_ventas_hoy = [v.id_venta for v in ventas_hoy]

    costo_total = Decimal('0.00')

    if ids_ventas_hoy:
        detalles_hoy = VentaDetalle.query.filter(
            VentaDetalle.venta_id.in_(ids_ventas_hoy)
        ).all()

        for det in detalles_hoy:
            producto = Productos.query.get(det.producto_id)
            if producto and producto.precio_base:
              
                receta = next(
                    (r for r in producto.recetas if r.es_active == 1), None
                )
                if receta:
                    costo_receta = Decimal('0.00')
                    for ingrediente in receta.detalles:
                        mp = ingrediente.materia_prima
                        if mp and mp.costo_unitario:
                            costo_receta += (
                                Decimal(str(ingrediente.cantidad)) *
                                Decimal(str(mp.costo_unitario))
                            )
                    # costo por unidad producida según receta
                    costo_unitario_real = (
                        costo_receta / receta.cuanto_produce
                        if receta.cuanto_produce > 0
                        else Decimal('0.00')
                    )
                    costo_total += costo_unitario_real * Decimal(str(det.cantidad))
                else:
                    # Fallback: estimado del 60% del precio base
                    costo_total += (
                        Decimal(str(det.precio_unitario)) *
                        Decimal('0.60') *
                        Decimal(str(det.cantidad))
                    )

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
        Venta.fecha_venta >= inicio_hoy,
        Venta.fecha_venta <= fin_hoy
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
        Venta.fecha_venta >= inicio_hoy,
        Venta.fecha_venta <= fin_hoy
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
        Venta.fecha_venta >= inicio_hoy,
        Venta.fecha_venta <= fin_hoy
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
        fecha_hoy        = hoy.strftime('%d/%m/%Y'),
        ventas_dia       = f'{ventas_dia:,.2f}',
        num_ventas       = num_ventas,
        ticket_promedio  = f'{ticket_promedio:,.2f}',
        utilidad_dia     = f'{utilidad_dia:,.2f}',
        productos_top    = productos_top,
        presentaciones_top = presentaciones_top,
        ventas_recientes = ventas_recientes,
    )

# ============================================================
# VENTAS
# ============================================================

@comercial_bp.route('/ventas')
@login_required
def ventas():
    form     = VentaForm()
    clientes = Cliente.query.filter_by(es_activo=1).order_by(Cliente.razon_social).all()
    prods    = Productos.query.filter_by(es_active=1).order_by(Productos.nombre).all()

    form.cliente_id.choices = [(c.id_cliente, c.razon_social) for c in clientes]

    hoy_ventas  = datetime.now()
    mes_actual  = hoy_ventas.month
    anio_actual = hoy_ventas.year

    # Calcular inicio y fin del mes actual para usar índice
    inicio_mes = datetime(anio_actual, mes_actual, 1)
    if mes_actual == 12:
        fin_mes = datetime(anio_actual + 1, 1, 1)
    else:
        fin_mes = datetime(anio_actual, mes_actual + 1, 1)

    ventas_mes_q = Venta.query.filter(
        Venta.fecha_venta >= inicio_mes,
        Venta.fecha_venta <  fin_mes
    ).all()

    ventas_mes      = sum(float(v.total) for v in ventas_mes_q)
    num_ventas      = len(ventas_mes_q)
    ticket_promedio = round(ventas_mes / num_ventas, 2) if num_ventas > 0 else 0
    cuentas_cobrar  = sum(float(v.total) for v in ventas_mes_q if v.estado == 'CREDITO')

    lista_ventas_q = Venta.query.order_by(Venta.fecha_creacion.desc()).limit(50).all()
    lista_ventas = [{
        'id': v.id_venta,
        'folio': v.folio,
        'cliente': v.cliente.razon_social if v.cliente else 'N/A',
        'num_productos': int(sum(d.cantidad for d in v.detalle)),
        'total': f'{v.total:,.2f}',
        'metodo_pago': v.metodo_pago.capitalize(),
        'fecha': v.fecha_venta.strftime('%d/%m/%Y'),
        'estado': v.estado.capitalize()
    } for v in lista_ventas_q]

    return render_template('comercial/ventas.html',
        form               = form,
        clientes           = clientes,
        productos          = prods,
        ventas             = lista_ventas,
        ventas_mes         = f'{ventas_mes:,.2f}',
        num_ventas         = num_ventas,
        ticket_promedio    = f'{ticket_promedio:,.2f}',
        cuentas_por_cobrar = f'{cuentas_cobrar:,.2f}',
    )

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
        flash('Completa todos los campos requeridos.', 'danger')
        return redirect(url_for('comercial_bp.ventas'))

    try:
        fecha_venta = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.now()

        folio = 'TEMP'

        subtotal      = Decimal('0.00')
        detalle_items = []

        for pid, cant_str, precio_str in zip(producto_ids, cantidades, precios):
         # Saltar filas vacías
            if not pid or not cant_str or not precio_str:
               continue

        # Validar y convertir cantidad
        try:
            cant = Decimal(str(cant_str).strip())
            if cant <= 0:
                raise Exception(f"La cantidad debe ser mayor a 0.")
        except Exception as e:
            raise Exception(f"Cantidad inválida '{cant_str}': {str(e)}")

        # Validar y convertir precio
        try:
            precio = Decimal(str(precio_str).strip())
            if precio < 0:
                raise Exception(f"El precio no puede ser negativo.")
        except Exception as e:
            raise Exception(f"Precio inválido '{precio_str}': {str(e)}")

        total_linea = cant * precio
        subtotal   += total_linea

        # Obtener nombre del producto para mensajes claros
        producto_obj = Productos.query.get(int(pid))
        nombre_producto = producto_obj.nombre if producto_obj else f"ID {pid}"

        # Validar existencia y stock
        existencia = Existencias.query.with_for_update().filter_by(producto_id=int(pid)).first()
        if not existencia:
            raise Exception(
                f"El producto '{nombre_producto}' no tiene registro de inventario."
            )
        if existencia.stock_actual < cant:
            raise Exception(
                f"Stock insuficiente para '{nombre_producto}': "
                f"disponible {float(existencia.stock_actual):.3f}, "
                f"solicitado {float(cant):.3f}."
            )

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

        venta.folio = f'V-{datetime.now().year}-{str(venta.id_venta).zfill(5)}'

        for pid, cant, precio, total_linea in detalle_items:
            det = VentaDetalle(
                venta_id        = venta.id_venta,
                producto_id     = pid,
                cantidad        = cant,
                precio_unitario = precio,
                total_linea     = total_linea,
            )
            db.session.add(det)

        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Venta", f"Venta registrada: {folio} por ${total:,.2f}")
        flash(f'Venta {folio} registrada correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la venta: {str(e)}', 'danger')

    return redirect(url_for('comercial_bp.ventas'))

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
        CorteCaja.periodo_inicio <= fin_hoy,
        CorteCaja.estado == 'ABIERTO'
    ).first()

    if corte_existente:
        flash('Ya existe un corte abierto para hoy. Ciérralo antes de iniciar uno nuevo.', 'warning')
        return redirect(url_for('comercial_bp.corte'))
    # ────────────────────────────────────────────────────────────

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
            producto = Productos.query.get(det.producto_id)
            if producto and producto.precio_base:
                receta = next((r for r in producto.recetas if r.es_active == 1), None)
                if receta:
                    costo_receta = sum((Decimal(str(ing.cantidad)) * Decimal(str(ing.materia_prima.costo_unitario))) for ing in receta.detalles if ing.materia_prima and ing.materia_prima.costo_unitario)
                    costo_unitario_real = costo_receta / receta.cuanto_produce if receta.cuanto_produce > 0 else Decimal('0.00')
                    costo_total_corte += costo_unitario_real * Decimal(str(det.cantidad))
                else:
                    # Fallback del 60% si no hay receta activa
                    costo_total_corte += Decimal(str(det.precio_unitario)) * Decimal('0.60') * Decimal(str(det.cantidad))

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