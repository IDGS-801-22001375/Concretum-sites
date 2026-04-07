from flask import render_template, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from models import db, Productos, Existencias, MovimientosInventario, MateriaPrima, ExistenciaMateriaPrima, Produccion
from . import inventario_bp
from sqlalchemy import or_, asc, desc, func
import datetime
from decimal import Decimal

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
@inventario_bp.route('/inventario')
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def index():
    return render_template('inventario/index.html')

# ----------------------------------------------------------------------
# API: PRODUCTOS TERMINADOS (con stock)
# ----------------------------------------------------------------------
@inventario_bp.route('/inventario/api/productos', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def api_productos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    query = Productos.query.filter_by(es_activo=True)
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
@inventario_bp.route('/inventario/api/materia-prima', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA')
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
# API: PRODUCCIONES EN PROCESO (estado EN_PROCESO)
# ----------------------------------------------------------------------
@inventario_bp.route('/inventario/api/producciones', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'GERENTE_PRODUCCION')
def api_producciones():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'fecha_inicio')
    sort_order = request.args.get('sort_order', 'desc')

    query = Produccion.query.filter(Produccion.estado == 'EN_PROCESO')
    if search:
        query = query.filter(Produccion.producto.has(Productos.nombre.ilike(f'%{search}%')))
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
# API: MOVIMIENTOS DE INVENTARIO (historial)
# ----------------------------------------------------------------------
@inventario_bp.route('/inventario/api/movimientos', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA')
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
        # Buscar por nombre de producto (a través de existencia.producto)
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
# REGISTRAR MOVIMIENTO (ENTRADA/SALIDA/AJUSTE)
# ----------------------------------------------------------------------
@inventario_bp.route('/inventario/movimiento', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO')
def registrar_movimiento():
    data = request.get_json()
    producto_id = data.get('producto_id')
    tipo = data.get('tipo')
    cantidad = float(data.get('cantidad', 0))
    motivo = data.get('motivo', '')

    if not producto_id or tipo not in ['ENTRADA', 'SALIDA', 'AJUSTE'] or cantidad <= 0:
        return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400

    # Obtener existencia del producto
    existencia = Existencias.query.filter_by(producto_id=producto_id).first()
    if not existencia:
        return jsonify({'success': False, 'message': 'Producto no encontrado en inventario.'}), 404

    # Validar stock suficiente para SALIDA
    if tipo == 'SALIDA' and existencia.stock_actual < cantidad:
        return jsonify({'success': False, 'message': 'Stock insuficiente.'}), 400

    cantidad_dec = Decimal(str(cantidad))
    if tipo == 'ENTRADA':
        existencia.stock_actual += cantidad_dec
    elif tipo == 'SALIDA':
        existencia.stock_actual -= cantidad_dec
    elif tipo == 'AJUSTE':
        existencia.stock_actual = cantidad_dec

    # Registrar movimiento
    movimiento = MovimientosInventario(
        existencia_id=existencia.id,
        usuario_id=current_user.id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo
    )
    db.session.add(movimiento)
    db.session.commit()

    registrar_auditoria(current_user.id, f"Movimiento {tipo}",
                        f"Producto ID {producto_id}, Cantidad: {cantidad}, Motivo: {motivo}")
    return jsonify({'success': True, 'message': 'Movimiento registrado correctamente.'})

# ----------------------------------------------------------------------
# OBTENER LISTA DE PRODUCTOS (para selector en movimientos)
# ----------------------------------------------------------------------
@inventario_bp.route('/inventario/productos-lista', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def productos_lista():
    productos = Productos.query.filter_by(es_activo=True).all()
    items = [{'id': p.id, 'nombre': f"{p.sku} - {p.nombre}", 'stock': float(p.existencia.stock_actual) if p.existencia else 0} for p in productos]
    return jsonify({'items': items})

# ----------------------------------------------------------------------
# KPIs GLOBALES (para el dashboard del inventario)
# ----------------------------------------------------------------------
@inventario_bp.route('/inventario/kpis', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA')
def kpis():
    # Total de productos activos
    total_productos = Productos.query.filter_by(es_activo=True).count()
    # Valor total del inventario (productos terminados)
    valor_total = db.session.query(func.sum(Existencias.stock_actual * Productos.precio_base)).join(Productos).filter(Productos.es_activo == True).scalar() or 0
    # Alertas: productos con stock menor a 10 (ejemplo)
    alertas = Existencias.query.filter(Existencias.stock_actual < 10).count()
    # Movimientos del mes
    inicio_mes = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    movimientos_mes = MovimientosInventario.query.filter(MovimientosInventario.fecha_creacion >= inicio_mes).count()
    return jsonify({
        'total_productos': total_productos,
        'valor_total': float(valor_total),
        'alertas': alertas,
        'movimientos_mes': movimientos_mes
    })