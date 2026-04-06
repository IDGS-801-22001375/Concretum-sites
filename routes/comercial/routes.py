from flask import render_template, request, redirect, url_for, flash
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

from extensions import db
from routes.comercial.models import Venta, VentaDetalle, CorteCaja, CorteDesglose, Cliente, Producto
from routes.comercial.forms import VentaForm, CorteForm, TicketForm
from routes.comercial import comercial_bp


# ============================================================
# DASHBOARD
# ============================================================

@comercial_bp.route('/dashboard')
def dashboard():
    hoy = date.today()

    ventas_hoy = Venta.query.filter(
        func.date(Venta.fecha_venta) == hoy
    ).all()

    ventas_dia      = sum(float(v.total) for v in ventas_hoy)
    num_ventas      = len(ventas_hoy)
    ticket_promedio = round(ventas_dia / num_ventas, 2) if num_ventas > 0 else 0
    utilidad_dia    = ventas_dia

    productos_top = db.session.query(
        Producto.nombre,
        Producto.id_producto,
        func.sum(VentaDetalle.cantidad).label('cantidad'),
        func.sum(VentaDetalle.total_linea).label('total')
    ).join(VentaDetalle, VentaDetalle.producto_id == Producto.id_producto)\
     .join(Venta, Venta.id_venta == VentaDetalle.venta_id)\
     .filter(func.date(Venta.fecha_venta) == hoy)\
     .group_by(Producto.id_producto, Producto.nombre)\
     .order_by(func.sum(VentaDetalle.cantidad).desc())\
     .limit(5).all()

    ventas_recientes = Venta.query\
        .filter(func.date(Venta.fecha_venta) == hoy)\
        .order_by(Venta.fecha_creacion.desc())\
        .limit(10).all()

    return render_template('comercial/dashboard.html',
        fecha_hoy        = hoy.strftime('%d/%m/%Y'),
        ventas_dia       = f'{ventas_dia:,.2f}',
        num_ventas       = num_ventas,
        ticket_promedio  = f'{ticket_promedio:,.2f}',
        utilidad_dia     = f'{utilidad_dia:,.2f}',
        productos_top    = productos_top,
        ventas_recientes = ventas_recientes,
    )


# ============================================================
# VENTAS
# ============================================================

@comercial_bp.route('/ventas')
def ventas():
    form     = VentaForm()
    clientes = Cliente.query.filter_by(es_activo=1).order_by(Cliente.razon_social).all()
    prods    = Producto.query.filter_by(es_activo=1).order_by(Producto.nombre).all()

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

    lista_ventas = Venta.query.order_by(Venta.fecha_creacion.desc()).limit(50).all()

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
            detalle_items.append((int(pid), cant, precio, total_linea))

        iva    = subtotal * Decimal('0.16')
        total  = subtotal + iva
        estado = 'CREDITO' if metodo_pago == 'CREDITO' else 'COBRADO'

        venta = Venta(
            folio       = folio,
            cliente_id  = cliente_id,
            metodo_pago = metodo_pago,
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
        flash(f'Venta {folio} registrada correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la venta: {str(e)}', 'danger')

    return redirect(url_for('comercial_bp.ventas'))


# ============================================================
# TICKET
# ============================================================

@comercial_bp.route('/ticket', methods=['GET'])
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


# ============================================================
# CORTE DE CAJA
# ============================================================

@comercial_bp.route('/corte')
def corte():
    form = CorteForm()
    hoy  = date.today()

    corte_activo = CorteCaja.query.filter(
        func.date(CorteCaja.periodo_inicio) == hoy,
        CorteCaja.estado == 'ABIERTO'
    ).first()

    ventas_hoy = Venta.query.filter(
        func.date(Venta.fecha_venta) == hoy
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

    historial_cortes = CorteCaja.query\
        .filter(CorteCaja.estado == 'CERRADO')\
        .order_by(CorteCaja.fecha_creacion.desc())\
        .limit(10).all()

    return render_template('comercial/corte.html',
        form               = form,
        periodo            = f'Hoy {hoy.strftime("%d/%m/%Y")}',
        cajero             = '—',
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
        flash('Corte iniciado correctamente.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('comercial_bp.corte'))


@comercial_bp.route('/corte/cerrar', methods=['POST'])
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
            flash('Corte cerrado correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    else:
        flash('No hay corte activo para cerrar.', 'warning')

    return redirect(url_for('comercial_bp.corte'))