from flask import render_template, request, jsonify, session
from flask_security import login_required, roles_accepted, current_user
from models import db, Merma, MateriaPrima, Producto, ExistenciaMateriaPrima, Existencia, MovimientoInventario
from . import mermas_bp
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
            "modulo": "Mermas",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

@mermas_bp.route('/mermas')
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_PRODUCCION', 'ALMACENISTA')
def index():
    return render_template('mermas/index.html')

@mermas_bp.route('/mermas/kpis')
@login_required
def kpis():
    from datetime import datetime, timedelta
    hoy = datetime.utcnow()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mermas_mes = Merma.query.filter(Merma.fecha_registro >= inicio_mes).all()
    total_registros = len(mermas_mes)
    valor_total = sum(float(m.valor_monetario) for m in mermas_mes)
    
    # Porcentaje respecto al valor total del inventario (aproximado)
    # Suma de existencias de productos + materia prima
    from sqlalchemy import func as sa_func
    valor_productos = db.session.query(sa_func.sum(Existencia.stock_actual * Producto.precio_base)).join(Producto).scalar() or 0
    valor_mp = db.session.query(sa_func.sum(ExistenciaMateriaPrima.stock_actual * MateriaPrima.costo_unitario)).join(MateriaPrima).scalar() or 0
    valor_inventario = float(valor_productos) + float(valor_mp)
    porcentaje = (valor_total / valor_inventario * 100) if valor_inventario > 0 else 0
    
    return jsonify({
        'total_registros': total_registros,
        'valor_total': valor_total,
        'porcentaje': round(porcentaje, 2)
    })

@mermas_bp.route('/mermas/api', methods=['GET'])
@login_required
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
        if m.tipo_material == 'MATERIA_PRIMA':
            material = MateriaPrima.query.get(m.material_id)
            nombre = material.nombre if material else 'Desconocido'
        else:
            material = Producto.query.get(m.material_id)
            nombre = material.nombre if material else 'Desconocido'
        
        items.append({
            'id': m.id,
            'fecha_registro': m.fecha_registro.strftime('%Y-%m-%d %H:%M'),
            'tipo_material': m.tipo_material,
            'material_nombre': nombre,
            'cantidad': float(m.cantidad),
            'causa': m.causa,
            'responsable': m.responsable,
            'valor_monetario': float(m.valor_monetario)
        })
    
    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@mermas_bp.route('/mermas/materiales-lista', methods=['GET'])
@login_required
def materiales_lista():
    tipo = request.args.get('tipo')
    if tipo == 'MATERIA_PRIMA':
        materiales = MateriaPrima.query.filter_by(es_activo=True).all()
        items = [{
            'id': m.id,
            'nombre': m.nombre,
            'stock': float(m.existencia.stock_actual) if m.existencia else 0,
            'costo': float(m.costo_unitario) if m.costo_unitario else 0
        } for m in materiales]
    else:
        productos = Producto.query.filter_by(es_activo=True).all()
        items = [{
            'id': p.id,
            'nombre': p.nombre,
            'stock': float(p.existencia.stock_actual) if p.existencia else 0,
            'costo': float(p.precio_base)
        } for p in productos]
    return jsonify({'items': items})

@mermas_bp.route('/mermas/registrar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_PRODUCCION', 'ALMACENISTA')
def registrar_merma():
    data = request.get_json()
    tipo = data.get('tipo_material')
    material_id = data.get('material_id')
    cantidad = float(data.get('cantidad'))
    causa = data.get('causa')
    responsable = data.get('responsable', '')
    observaciones = data.get('observaciones', '')
    
    if not tipo or not material_id or cantidad <= 0 or not causa:
        return jsonify({'success': False, 'message': 'Faltan datos obligatorios'}), 400
    
    # Obtener costo unitario y actualizar stock
    movimiento_id = None
    if tipo == 'MATERIA_PRIMA':
        material = MateriaPrima.query.get(material_id)
        if not material:
            return jsonify({'success': False, 'message': 'Material no encontrado'}), 404
        costo = float(material.costo_unitario) if material.costo_unitario else 0
        existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=material.id).first()
        if not existencia:
            return jsonify({'success': False, 'message': 'No hay registro de existencia para este material'}), 400
        cantidad_dec = Decimal(str(cantidad))
        if existencia.stock_actual < cantidad_dec:
            return jsonify({'success': False, 'message': 'Cantidad de merma supera el stock disponible'}), 400
        existencia.stock_actual -= cantidad_dec
        movimiento_id = None
    else:
        material = Producto.query.get(material_id)
        if not material:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        costo = float(material.precio_base) if material.precio_base else 0
        existencia = Existencia.query.filter_by(producto_id=material.id).first()
        if not existencia:
            return jsonify({'success': False, 'message': 'No hay registro de existencia para este producto'}), 400
        cantidad_dec = Decimal(str(cantidad))
        if existencia.stock_actual < cantidad_dec:
            return jsonify({'success': False, 'message': 'Cantidad de merma supera el stock disponible'}), 400
        existencia.stock_actual -= cantidad_dec
        # Crear movimiento de inventario
        movimiento = MovimientoInventario(
            existencia_id=existencia.id,
            usuario_id=current_user.id,
            tipo='SALIDA',
            cantidad=cantidad_dec,
            motivo=f'Merma por {causa}: {observaciones[:200]}'
        )
        db.session.add(movimiento)
        db.session.flush()
        movimiento_id = movimiento.id

    valor_monetario = cantidad * costo
    
    merma = Merma(
        tipo_material=tipo,
        material_id=material_id,
        cantidad=cantidad,
        causa=causa,
        responsable=responsable,
        observaciones=observaciones,
        valor_monetario=valor_monetario,
        usuario_id=current_user.id,
        movimiento_id=movimiento_id
    )
    db.session.add(merma)
    db.session.commit()
    
    registrar_auditoria(current_user.id, "Registrar Merma", 
                        f"{tipo} {material.nombre} - Cantidad: {cantidad} - Causa: {causa}")
    
    return jsonify({'success': True, 'message': 'Merma registrada correctamente'})