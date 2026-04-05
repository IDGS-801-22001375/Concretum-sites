from flask import render_template, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from models import db, Merma, MateriaPrima, Producto, Existencia, ExistenciaMateriaPrima, MovimientoInventario
from . import mermas_bp
from sqlalchemy import func, desc
from decimal import Decimal
import datetime

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Mermas",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

# ----------------------------------------------------------------------
# VISTA PRINCIPAL
# ----------------------------------------------------------------------
@mermas_bp.route('/mermas')
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA', 'GERENTE_PRODUCCION')
def index():
    return render_template('mermas/index.html')

# ----------------------------------------------------------------------
# API: LISTAR MERMAS (paginado)
# ----------------------------------------------------------------------
@mermas_bp.route('/mermas/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA', 'GERENTE_PRODUCCION')
def api_mermas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    tipo = request.args.get('tipo', '')
    causa = request.args.get('causa', '')

    query = Merma.query
    if search:
        query = query.filter(Merma.responsable.ilike(f'%{search}%'))
    if tipo:
        query = query.filter(Merma.tipo_material == tipo)
    if causa:
        query = query.filter(Merma.causa == causa)

    query = query.order_by(desc(Merma.fecha_registro))
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for m in paginated.items:
        # Obtener nombre del material según tipo
        nombre_material = ''
        if m.tipo_material == 'MATERIA_PRIMA':
            mp = MateriaPrima.query.get(m.material_id)
            nombre_material = mp.nombre if mp else 'Desconocido'
        else:
            prod = Producto.query.get(m.material_id)
            nombre_material = prod.nombre if prod else 'Desconocido'

        items.append({
            'id': m.id,
            'fecha_registro': m.fecha_registro.strftime('%Y-%m-%d %H:%M'),
            'tipo_material': m.tipo_material,
            'material_nombre': nombre_material,
            'cantidad': float(m.cantidad),
            'causa': m.causa,
            'responsable': m.responsable or '',
            'observaciones': m.observaciones or '',
            'valor_monetario': float(m.valor_monetario)
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

# ----------------------------------------------------------------------
# API: OBTENER LISTAS PARA SELECTORES (materias primas y productos)
# ----------------------------------------------------------------------
@mermas_bp.route('/mermas/materiales-lista', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA', 'GERENTE_PRODUCCION')
def materiales_lista():
    tipo = request.args.get('tipo')
    if tipo == 'MATERIA_PRIMA':
        materiales = MateriaPrima.query.filter_by(es_activo=True).all()
        items = [{
            'id': m.id,
            'nombre': f"{m.sku} - {m.nombre}",
            'stock': float(m.existencia.stock_actual) if m.existencia else 0,
            'costo': float(m.costo_unitario)
        } for m in materiales]
    else:  # PRODUCTO
        productos = Producto.query.filter_by(es_activo=True).all()
        items = [{
            'id': p.id,
            'nombre': f"{p.sku} - {p.nombre}",
            'stock': float(p.existencia.stock_actual) if p.existencia else 0,
            'costo': float(p.precio_base)
        } for p in productos]
    return jsonify({'items': items})

# ----------------------------------------------------------------------
# REGISTRAR MERMA
# ----------------------------------------------------------------------
@mermas_bp.route('/mermas/registrar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO')
def registrar_merma():
    data = request.get_json()
    tipo = data.get('tipo_material')
    material_id = data.get('material_id')
    cantidad = float(data.get('cantidad', 0))
    causa = data.get('causa')
    responsable = data.get('responsable', '')
    observaciones = data.get('observaciones', '')

    if not tipo or not material_id or cantidad <= 0 or not causa:
        return jsonify({'success': False, 'message': 'Datos incompletos.'}), 400

    # Obtener costo unitario y actualizar stock
    if tipo == 'MATERIA_PRIMA':
        material = MateriaPrima.query.get(material_id)
        if not material or not material.es_activo:
            return jsonify({'success': False, 'message': 'Materia prima no válida.'}), 400
        costo = float(material.costo_unitario)
        existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=material_id).first()
        if not existencia or existencia.stock_actual < cantidad:
            return jsonify({'success': False, 'message': 'Stock insuficiente para registrar merma.'}), 400
        # Actualizar stock
        existencia.stock_actual -= Decimal(str(cantidad))
        # Registrar movimiento de inventario
        movimiento = MovimientoInventario(
            existencia_id=None,  # Para materia prima no usamos existencia de producto
            usuario_id=current_user.id,
            tipo='SALIDA',
            cantidad=cantidad,
            motivo=f'Merma por {causa}: {observaciones[:200]}'
        )
        # Nota: No asociamos movimiento a existencia de producto, pero lo guardamos igual para auditoría.
        # Podríamos crear una tabla de movimientos de materia prima, pero por simplicidad usamos esta.
        # Lo guardamos sin existencia_id (permitido).
        db.session.add(movimiento)
        db.session.flush()
    else:  # PRODUCTO
        producto = Producto.query.get(material_id)
        if not producto or not producto.es_activo:
            return jsonify({'success': False, 'message': 'Producto no válido.'}), 400
        costo = float(producto.precio_base)
        existencia = Existencia.query.filter_by(producto_id=material_id).first()
        if not existencia or existencia.stock_actual < cantidad:
            return jsonify({'success': False, 'message': 'Stock insuficiente para registrar merma.'}), 400
        existencia.stock_actual -= Decimal(str(cantidad))
        movimiento = MovimientoInventario(
            existencia_id=existencia.id,
            usuario_id=current_user.id,
            tipo='SALIDA',
            cantidad=cantidad,
            motivo=f'Merma por {causa}: {observaciones[:200]}'
        )
        db.session.add(movimiento)
        db.session.flush()

    valor = cantidad * costo

    # Crear registro de merma
    merma = Merma(
        tipo_material=tipo,
        material_id=material_id,
        cantidad=cantidad,
        causa=causa,
        responsable=responsable,
        observaciones=observaciones,
        valor_monetario=valor,
        usuario_id=current_user.id,
        movimiento_id=movimiento.id if movimiento else None
    )
    db.session.add(merma)
    db.session.commit()

    registrar_auditoria(current_user.id, "Registrar Merma",
                        f"{tipo} ID {material_id}, Cantidad: {cantidad}, Causa: {causa}, Valor: {valor}")
    return jsonify({'success': True, 'message': 'Merma registrada correctamente.'})

# ----------------------------------------------------------------------
# KPIS PARA EL DASHBOARD DE MERMAS
# ----------------------------------------------------------------------
@mermas_bp.route('/mermas/kpis', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_INVENTARIO', 'ALMACENISTA', 'GERENTE_PRODUCCION')
def kpis():
    hoy = datetime.date.today()
    inicio_mes = datetime.datetime(hoy.year, hoy.month, 1)
    # Total de mermas del mes
    total_registros = Merma.query.filter(Merma.fecha_registro >= inicio_mes).count()
    # Valor total de mermas del mes
    valor_total = db.session.query(func.sum(Merma.valor_monetario)).filter(Merma.fecha_registro >= inicio_mes).scalar() or 0
    # Calcular % de merma: (valor_total / valor_produccion_mes) * 100
    # Para simplificar, mostraremos solo el valor total y un placeholder del porcentaje
    # Se puede calcular después con datos de producción.
    # Por ahora, calculamos % respecto al valor total de inventario o lo dejamos como 'N/A'
    porcentaje = 0.0
    # Obtener valor total del inventario (productos terminados)
    valor_inventario = db.session.query(func.sum(Existencia.stock_actual * Producto.precio_base)).join(Producto).filter(Producto.es_activo == True).scalar() or 0
    if valor_inventario > 0:
        porcentaje = (float(valor_total) / float(valor_inventario)) * 100

    return jsonify({
        'total_registros': total_registros,
        'valor_total': float(valor_total),
        'porcentaje': round(porcentaje, 2)
    })