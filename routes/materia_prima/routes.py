from flask import render_template, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from models import db, MateriaPrima, ExistenciaMateriaPrima, Proveedor
from . import materia_prima_bp
from sqlalchemy import or_, asc, desc
import datetime
import threading
from copy import copy

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
        "modulo": "Nombre del Modulo",
        "user_agent": user_agent,
        "ip": ip_addr,
        "fecha_creacion": datetime.datetime.utcnow()
    }
    
    threading.Thread(target=_guardar_en_mongo, args=(datos_auditoria,)).start()

@materia_prima_bp.route('/materia-prima')
@login_required
@roles_accepted('ADMINISTRADOR', 'ALMACEN')
def index():
    proveedores = Proveedor.query.filter_by(es_activo=True).all()
    proveedores_options = [{'value': p.id, 'label': p.razon_social} for p in proveedores]
    return render_template('materia_prima/index.html', proveedores_options=proveedores_options)

@materia_prima_bp.route('/materia-prima/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ALMACEN')
def api_materia_prima():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')
    search = request.args.get('search', '')
    active_filter = request.args.get('active', '')

    query = MateriaPrima.query

    if search:
        query = query.filter(or_(
            MateriaPrima.nombre.ilike(f'%{search}%'),
            MateriaPrima.sku.ilike(f'%{search}%')
        ))
    if active_filter:
        if active_filter == 'true':
            query = query.filter(MateriaPrima.es_activo == True)
        elif active_filter == 'false':
            query = query.filter(MateriaPrima.es_activo == False)

    # Ordenamiento
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(MateriaPrima, sort_by, MateriaPrima.nombre)))
    else:
        query = query.order_by(desc(getattr(MateriaPrima, sort_by, MateriaPrima.nombre)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for mp in paginated.items:
        stock = mp.existencia.stock_actual if mp.existencia else 0
        items.append({
            'id': mp.id,
            'sku': mp.sku,
            'nombre': mp.nombre,
            'unidad_medida': mp.unidad_medida,
            'proveedor_id': mp.proveedor_id,
            'proveedor_nombre': mp.proveedor.razon_social if mp.proveedor else 'N/A',
            'stock_minimo': float(mp.stock_minimo),
            'costo_unitario': float(mp.costo_unitario),
            'stock': float(stock),
            'es_activo': mp.es_activo
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@materia_prima_bp.route('/materia-prima/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ALMACEN')
def guardar_materia_prima():
    data = request.form
    id_mp = data.get('id_materia_prima')
    if id_mp:
        # Editar
        mp = MateriaPrima.query.get_or_404(int(id_mp))
        mp.sku = data['sku']
        mp.nombre = data['nombre']
        mp.unidad_medida = data['unidad_medida']
        mp.proveedor_id = data['proveedor_id']
        mp.stock_minimo = float(data.get('stock_minimo', 0))
        mp.costo_unitario = float(data.get('costo_unitario', 0))
        db.session.commit()
        registrar_auditoria(current_user.id, "Editar Materia Prima", f"Materia prima editada: {mp.nombre}")
        return jsonify({'success': True, 'message': 'Materia prima actualizada.'})
    else:
        # Crear
        if MateriaPrima.query.filter_by(sku=data['sku']).first():
            return jsonify({'success': False, 'errors': {'sku': 'El SKU ya existe.'}}), 400
        mp = MateriaPrima(
            sku=data['sku'],
            nombre=data['nombre'],
            unidad_medida=data['unidad_medida'],
            proveedor_id=data['proveedor_id'],
            stock_minimo=float(data.get('stock_minimo', 0)),
            costo_unitario=float(data.get('costo_unitario', 0)),
            es_activo=True
        )
        db.session.add(mp)
        db.session.flush()  # para obtener el id
        # Crear registro de existencia asociado
        existencia = ExistenciaMateriaPrima(materia_prima_id=mp.id, stock_actual=0)
        db.session.add(existencia)
        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Materia Prima", f"Materia prima creada: {mp.nombre}")
        return jsonify({'success': True, 'message': 'Materia prima creada.'})

@materia_prima_bp.route('/materia-prima/obtener/<int:id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ALMACEN')
def obtener_materia_prima(id):
    mp = MateriaPrima.query.get_or_404(id)
    return jsonify({
        'id': mp.id,
        'sku': mp.sku,
        'nombre': mp.nombre,
        'unidad_medida': mp.unidad_medida,
        'proveedor_id': mp.proveedor_id,
        'stock_minimo': float(mp.stock_minimo),
        'costo_unitario': float(mp.costo_unitario),
        'es_activo': mp.es_activo
    })

@materia_prima_bp.route('/materia-prima/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'ALMACEN')
def alternar_estado(id):
    mp = MateriaPrima.query.get_or_404(id)
    mp.es_activo = not mp.es_activo
    estado_txt = "Activado" if mp.es_activo else "Desactivado"
    registrar_auditoria(current_user.id, "Estado Materia Prima", f"Materia prima {mp.nombre} {estado_txt}")
    db.session.commit()
    return jsonify({'success': True, 'message': f'Materia prima {estado_txt.lower()} correctamente.'})