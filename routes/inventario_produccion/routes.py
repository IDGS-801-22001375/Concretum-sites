from flask_security import login_required, roles_accepted, current_user
from routes.inventario_produccion import stock_bp
from flask import render_template, request, redirect, url_for, flash, jsonify
from models import db, Existencias, Productos, MovimientosInventario, MateriaPrima, ExistenciaMateriaPrima, Produccion
from decimal import Decimal
from sqlalchemy import or_, asc, desc, func
import datetime


def obtener_productos(page=1):
    pagination = db.session.query(Existencias)\
        .join(Productos, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .paginate(page=page, per_page=5)

    todas = db.session.query(Existencias)\
        .join(Productos, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .all()

    bajo_stock = sum(1 for e in todas if e.estado_stock == 'BAJO')
    precaucion = sum(1 for e in todas if e.estado_stock == 'PRECAUCION')
    stock_ok   = sum(1 for e in todas if e.estado_stock == 'ALTO')

    return pagination, pagination.items, bajo_stock, precaucion, stock_ok


# =========================
# OBTENER STOCK (para HTML)
# =========================
@stock_bp.route('/stock-productos')
@login_required
def get_stock():
    page = request.args.get('page', 1, type=int)
    pagination, productos, bajo_stock, precaucion, stock_ok = obtener_productos(page)

    return render_template(
        'produccion/inventario/inventario.html',
        productos=productos,
        pagination=pagination,
        bajo_stock=bajo_stock,
        precaucion=precaucion,
        stock_ok=stock_ok
    )


# =========================
# EDITAR STOCK (SET DIRECTO)
# =========================
@stock_bp.route('/editar-stock/<int:id>', methods=['POST'])
@login_required
def editar_stock(id):
    existencia = Existencias.query.get_or_404(id)

    try:
        nuevo_stock = Decimal(request.form.get('stock', 0))
        diferencia = nuevo_stock - existencia.stock_actual

        if diferencia != 0:
            movimiento = MovimientosInventario(
                existencia_id=existencia.id_existencias,
                tipo='AJUSTE',
                cantidad=abs(diferencia),
                motivo='Edición directa de stock'
            )
            existencia.stock_actual = nuevo_stock
            db.session.add(movimiento)
            db.session.commit()
            db.session.refresh(existencia)

        flash('Stock actualizado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar stock: {str(e)}', 'error')

    return redirect(url_for('stock_bp.get_stock'))


# =========================
# AJUSTAR STOCK (+ / -)
# =========================
@stock_bp.route('/ajustar-stock/<int:id>', methods=['POST'])
@login_required
def ajustar_stock(id):
    existencia = Existencias.query.get_or_404(id)

    try:
        tipo     = request.form.get('tipo')
        cantidad = Decimal(request.form.get('cantidad', 0))

        if cantidad <= 0:
            flash('Cantidad inválida', 'error')
            return redirect(url_for('stock_bp.get_stock'))

        if tipo == 'entrada':
            existencia.stock_actual += cantidad
            tipo_mov = 'AJUSTE'

        elif tipo == 'salida':
            if cantidad > existencia.stock_actual:
                flash('No puedes sacar más de lo disponible', 'error')
                return redirect(url_for('stock_bp.get_stock'))
            existencia.stock_actual -= cantidad
            tipo_mov = 'SALIDA'

        else:
            flash('Tipo inválido', 'error')
            return redirect(url_for('stock_bp.get_stock'))

        movimiento = MovimientosInventario(
            existencia_id=existencia.id_existencias,
            tipo=tipo_mov,
            cantidad=cantidad,
            motivo='Ajuste manual'
        )
        db.session.add(movimiento)
        db.session.commit()
        db.session.refresh(existencia)

        flash('Ajuste aplicado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error en ajuste: {str(e)}', 'error')

    return redirect(url_for('stock_bp.get_stock'))


# =========================
# OBTENER STOCK ACTUAL (JSON)
# =========================
@stock_bp.route('/stock-actual/<int:id>', methods=['GET'])
@login_required
def obtener_stock_actual(id):
    existencia = Existencias.query.get_or_404(id)

    return {
        "producto":     existencia.producto.nombre,
        "stock_actual": float(existencia.stock_actual),
        "estado_stock": existencia.estado_stock
    }

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Inventario General",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}") 

# ----------------------------------------------------------------------
# VISTA PRINCIPAL
# ----------------------------------------------------------------------
@stock_bp.route('/inventario')
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def index():
    return render_template('inventario/index.html')


# ----------------------------------------------------------------------
# API: PRODUCTOS TERMINADOS (con stock)
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/api/productos', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def api_productos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    query = Productos.query.filter(Productos.es_active == 1)
    if search:
        query = query.filter(or_(
            Productos.nombre.ilike(f'%{search}%'),
            Productos.sku.ilike(f'%{search}%')
        ))

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Productos, sort_by, Productos.nombre)))
    else:
        query = query.order_by(desc(getattr(Productos, sort_by, Productos.nombre)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for p in paginated.items:
        existencia = Existencias.query.filter_by(producto_id=p.id).first()
        stock = float(existencia.stock_actual) if existencia else 0

        items.append({
            'id': p.id,
            'sku': p.sku,
            'nombre': p.nombre,
            'unidad_medida': p.unidad_medida,
            'precio_base': float(p.precio_base),
            'stock': stock,
            'valor_inventario': stock * float(p.precio_base)
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })


# ----------------------------------------------------------------------
# API: MATERIA PRIMA (stock actual)
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/api/materia-prima', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def api_materia_prima():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    query = MateriaPrima.query.filter_by(es_activo=True)

    if search:
        query = query.filter(or_(
            MateriaPrima.nombre.ilike(f'%{search}%'),
            MateriaPrima.sku.ilike(f'%{search}%')
        ))

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(MateriaPrima, sort_by, MateriaPrima.nombre)))
    else:
        query = query.order_by(desc(getattr(MateriaPrima, sort_by, MateriaPrima.nombre)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for mp in paginated.items:
        existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=mp.id).first()
        stock = float(existencia.stock_actual) if existencia else 0

        items.append({
            'id': mp.id,
            'sku': mp.sku,
            'nombre': mp.nombre,
            'unidad_medida': mp.unidad_medida,
            'costo_unitario': float(mp.costo_unitario),
            'stock': stock,
            'valor_inventario': stock * float(mp.costo_unitario)
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })


# ----------------------------------------------------------------------
# API: PRODUCCIONES EN PROCESO
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/api/producciones', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'GERENTE_PRODUCCION')
def api_producciones():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'fecha_inicio')
    sort_order = request.args.get('sort_order', 'desc')

    query = Produccion.query.filter(Produccion.estado == 'EN_PROCESO')

    if search:
        query = query.filter(
            Produccion.producto.has(Productos.nombre.ilike(f'%{search}%'))
        )

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Produccion, sort_by, Produccion.fecha_inicio)))
    else:
        query = query.order_by(desc(getattr(Produccion, sort_by, Produccion.fecha_inicio)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for prod in paginated.items:
        items.append({
            'id': prod.id,
            'producto_nombre': prod.producto.nombre,
            'cantidad_producida': float(prod.cantidad_producida),
            'unidad_medida': prod.unidad_medida,
            'fecha_inicio': prod.fecha_inicio.strftime('%Y-%m-%d %H:%M'),
            'estado': prod.estado
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })


# ----------------------------------------------------------------------
# API: MOVIMIENTOS DE INVENTARIO
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/api/movimientos', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def api_movimientos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tipo = request.args.get('tipo', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'fecha_creacion')
    sort_order = request.args.get('sort_order', 'desc')

    query = MovimientosInventario.query

    if tipo:
        query = query.filter(MovimientosInventario.tipo == tipo)

    if search:
        query = query.filter(
            MovimientosInventario.existencia.has(
                Productos.nombre.ilike(f'%{search}%')
            )
        )

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(MovimientosInventario, sort_by, MovimientosInventario.fecha_creacion)))
    else:
        query = query.order_by(desc(getattr(MovimientosInventario, sort_by, MovimientosInventario.fecha_creacion)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for mov in paginated.items:
        items.append({
            'id': mov.id,
            'producto_nombre': mov.existencia.producto.nombre if mov.existencia else 'N/A',
            'tipo': mov.tipo,
            'cantidad': float(mov.cantidad),
            'motivo': mov.motivo,
            'usuario': mov.usuario.username if mov.usuario else 'Sistema',
            'fecha': mov.fecha_creacion.strftime('%Y-%m-%d %H:%M')
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })


# ----------------------------------------------------------------------
# REGISTRAR MOVIMIENTO
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/movimiento', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO')
def registrar_movimiento():
    data = request.get_json()

    producto_id = data.get('producto_id')
    tipo = data.get('tipo')
    cantidad = float(data.get('cantidad', 0))
    motivo = data.get('motivo', '')

    if not producto_id or tipo not in ['ENTRADA', 'SALIDA', 'AJUSTE'] or cantidad <= 0:
        return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400

    existencia = Existencias.query.filter_by(producto_id=producto_id).first()
    if not existencia:
        return jsonify({'success': False, 'message': 'Producto no encontrado en inventario.'}), 404

    if tipo == 'SALIDA' and existencia.stock_actual < cantidad:
        return jsonify({'success': False, 'message': 'Stock insuficiente.'}), 400

    cantidad_dec = Decimal(str(cantidad))

    if tipo == 'ENTRADA':
        existencia.stock_actual += cantidad_dec
    elif tipo == 'SALIDA':
        existencia.stock_actual -= cantidad_dec
    elif tipo == 'AJUSTE':
        existencia.stock_actual = cantidad_dec

    movimiento = MovimientosInventario(
        existencia_id=existencia.id,
        usuario_id=current_user.id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo
    )

    db.session.add(movimiento)
    db.session.commit()

    registrar_auditoria(
        current_user.id,
        f"Movimiento {tipo}",
        f"Producto ID {producto_id}, Cantidad: {cantidad}, Motivo: {motivo}"
    )

    return jsonify({'success': True, 'message': 'Movimiento registrado correctamente.'})


# ----------------------------------------------------------------------
# LISTA DE PRODUCTOS
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/productos-lista', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def productos_lista():
    productos = Productos.query.filter(Productos.es_active == 1).all()

    items = [
        {
            'id': p.id,
            'nombre': f"{p.sku} - {p.nombre}",
            'stock': float(p.existencia.stock_actual) if p.existencia else 0
        }
        for p in productos
    ]

    return jsonify({'items': items})


# ----------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------
@stock_bp.route('/inventario/kpis', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ADMIN', 'SUPER_ADMIN', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def kpis():
    total_productos = Productos.query.filter_by(es_activo=True).count()

    valor_total = db.session.query(
        func.sum(Existencias.stock_actual * Productos.precio_base)
    ).join(Productos).filter(Productos.es_activo == True).scalar() or 0

    alertas = Existencias.query.filter(Existencias.stock_actual < 10).count()

    inicio_mes = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    movimientos_mes = MovimientosInventario.query.filter(
        MovimientosInventario.fecha_creacion >= inicio_mes
    ).count()

    return jsonify({
        'total_productos': total_productos,
        'valor_total': float(valor_total),
        'alertas': alertas,
        'movimientos_mes': movimientos_mes
    })