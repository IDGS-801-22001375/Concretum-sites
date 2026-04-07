from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func
from flask_security import login_required, roles_accepted, current_user

from models import db, Venta, VentaDetalle, CorteCaja, CorteDesglose, Cliente, Productos, Existencias, MovimientosInventario, User, CategoriasProducto
from forms import VentaForm, CorteForm, TicketForm
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

    ventas_hoy = Venta.query.filter(func.date(Venta.fecha_venta) == hoy).all()

    ventas_dia      = sum(float(v.total) for v in ventas_hoy)
    num_ventas      = len(ventas_hoy)
    ticket_promedio = round(ventas_dia / num_ventas, 2) if num_ventas > 0 else 0
    utilidad_dia    = ventas_dia * 0.35 # Calculo estimado del 35% de margen

    # Productos más vendidos
    productos_top = db.session.query(
        Productos.nombre,
        CategoriasProducto.nombre.label('categoria'),
        func.sum(VentaDetalle.cantidad).label('cantidad'),
        func.sum(VentaDetalle.total_linea).label('total')
    ).join(VentaDetalle, VentaDetalle.producto_id == Productos.id_producto)\
     .join(CategoriasProducto, Productos.categoria_id == CategoriasProducto.id_categoria)\
     .join(Venta, Venta.id_venta == VentaDetalle.venta_id)\
     .filter(func.date(Venta.fecha_venta) == hoy)\
     .group_by(Productos.id_producto, Productos.nombre, CategoriasProducto.nombre)\
     .order_by(func.sum(VentaDetalle.cantidad).desc())\
     .limit(5).all()

    # Presentaciones / Categorías más vendidas para las barras de progreso
    categorias_top = db.session.query(
        CategoriasProducto.nombre,
        func.sum(VentaDetalle.cantidad).label('cantidad')
    ).join(Productos, Productos.categoria_id == CategoriasProducto.id_categoria)\
     .join(VentaDetalle, VentaDetalle.producto_id == Productos.id_producto)\
     .join(Venta, Venta.id_venta == VentaDetalle.venta_id)\
     .filter(func.date(Venta.fecha_venta) == hoy)\
     .group_by(CategoriasProducto.nombre)\
     .order_by(func.sum(VentaDetalle.cantidad).desc())\
     .limit(4).all()

    total_unidades = sum(c.cantidad for c in categorias_top) if categorias_top else 1
    presentaciones_top = [{
        'nombre': c.nombre, 
        'cantidad': int(c.cantidad), 
        'porcentaje': round((c.cantidad / total_unidades) * 100)
    } for c in categorias_top]

    # Últimas ventas formateadas para la tabla
    ventas_recientes_q = Venta.query.filter(func.date(Venta.fecha_venta) == hoy).order_by(Venta.fecha_creacion.desc()).limit(10).all()
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

    mes_actual  = datetime.now().month
    anio_actual = datetime.now().year

    ventas_mes_q = Venta.query.filter(
        func.month(Venta.fecha_venta) == mes_actual,
        func.year(Venta.fecha_venta)  == anio_actual
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

        ultimo = Venta.query.order_by(Venta.id_venta.desc()).first()
        num    = (ultimo.id_venta + 1) if ultimo else 1
        folio  = f'V-{datetime.now().year}-{str(num).zfill(4)}'

        subtotal      = Decimal('0.00')
        detalle_items = []

        for pid, cant, precio in zip(producto_ids, cantidades, precios):
            if not pid or not cant or not precio:
                continue
            
            cant        = Decimal(cant)
            precio      = Decimal(precio)
            total_linea = cant * precio
            subtotal   += total_linea
            
            existencia = Existencias.query.filter_by(producto_id=int(pid)).first()
            if not existencia or existencia.stock_actual < cant:
                raise Exception(f"Stock insuficiente para el producto seleccionado.")
            
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
    form         = TicketForm()
    lista_ventas = Venta.query.order_by(Venta.fecha_creacion.desc()).all()

    form.venta_id.choices = [
        (v.id_venta, f'{v.folio} — {v.cliente.razon_social}')
        for v in lista_ventas
    ] if lista_ventas else [(0, 'Sin ventas')]

    venta_id = request.args.get('venta_id', type=int)
    venta    = Venta.query.get(venta_id) if venta_id else None

    return render_template('comercial/ticket.html',
        form   = form,
        ventas = lista_ventas,
        venta  = venta,
    )

@comercial_bp.route('/ticket/generar', methods=['POST'])
@login_required
def generar_ticket():
    form = TicketForm()
    lista_ventas = Venta.query.all()
    form.venta_id.choices = [(v.id_venta, v.folio) for v in lista_ventas]

    if form.validate_on_submit():
        venta = Venta.query.get_or_404(form.venta_id.data)
        tipo_doc = form.tipo.data
        
        registrar_auditoria(current_user.id, "Generar Documento", f"Generado {tipo_doc} para venta {venta.folio}")
        flash(f'{tipo_doc.capitalize()} generado para el folio {venta.folio}.', 'success')
        return redirect(url_for('comercial_bp.ticket', venta_id=venta.id_venta))
        
    flash('Error al generar el documento. Verifica los datos.', 'danger')
    return redirect(url_for('comercial_bp.ticket'))

# ============================================================
# CORTE DE CAJA
# ============================================================

@comercial_bp.route('/corte')
@login_required
def corte():
    form = CorteForm()
    hoy  = date.today()

    corte_activo = CorteCaja.query.filter(
        func.date(CorteCaja.periodo_inicio) == hoy,
        CorteCaja.estado == 'ABIERTO'
    ).first()

    ventas_hoy = Venta.query.filter(func.date(Venta.fecha_venta) == hoy).all()

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

    ventas_hoy     = Venta.query.filter(func.date(Venta.fecha_venta) == hoy).all()
    total_ventas   = sum(float(v.total) for v in ventas_hoy)
    total_cobrado  = sum(float(v.total) for v in ventas_hoy if v.estado == 'COBRADO')
    ventas_credito = sum(float(v.total) for v in ventas_hoy if v.estado == 'CREDITO')
    utilidad       = total_cobrado - fondo_inicial

    try:
        nuevo_corte = CorteCaja(
            usuario_id     = current_user.id,
            periodo_inicio = datetime.combine(hoy, datetime.min.time()),
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
    corte_activo = CorteCaja.query.filter(
        func.date(CorteCaja.periodo_inicio) == hoy,
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