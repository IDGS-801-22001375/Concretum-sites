from flask import render_template, request, jsonify, url_for
from flask_security import login_required, roles_accepted, current_user
from models import db, Recetas, RecetaDetalle, Productos, MateriaPrima, UnidadMedida
from . import recetas_bp
from sqlalchemy import or_, asc, desc
import datetime
import json
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
        "modulo": "Recetas",
        "user_agent": user_agent,
        "ip": ip_addr,
        "fecha_creacion": datetime.datetime.utcnow()
    }
    
    threading.Thread(target=_guardar_en_mongo, args=(datos_auditoria,)).start()

@recetas_bp.route('/recetas')
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def get_recetas():
    total = Recetas.query.count()
    activas = Recetas.query.filter_by(es_active=1).count()
    kpis = {'total': total, 'activas': activas}

    productos = Productos.query.filter_by(es_active=1).all()
    productos_options = [{'value': p.id_producto, 'label': f"{p.sku} - {p.nombre}"} for p in productos]

    productos_json = [{'id': p.id_producto, 'tiene_receta': any(r.es_active == 1 for r in p.recetas)} for p in productos]

    mp = MateriaPrima.query.filter_by(es_activo=True).all()
    mp_options = [{'value': m.id_materia_prima, 'label': f"{m.sku} - {m.nombre}"} for m in mp]

    unidades = UnidadMedida.query.filter_by(es_active=True).all()
    unidades_options = [{'value': u.id_unidad, 'label': u.nombre} for u in unidades]

    return render_template('produccion/recetas/recetas.html',
                           kpis=kpis,
                           productos_options=productos_options,
                           productos_json=productos_json, 
                           mp_options=mp_options,
                           unidades_options=unidades_options)

@recetas_bp.route('/recetas/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def api_recetas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'descripcion')
    sort_order = request.args.get('sort_order', 'asc')
    search = request.args.get('search', '')

    query = Recetas.query
    if search:
        query = query.filter(or_(
            Recetas.descripcion.ilike(f'%{search}%'),
            Recetas.producto.has(Productos.nombre.ilike(f'%{search}%'))
        ))

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Recetas, sort_by, Recetas.descripcion)))
    else:
        query = query.order_by(desc(getattr(Recetas, sort_by, Recetas.descripcion)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for r in paginated.items:
        items.append({
            'id': r.id_receta,
            'producto_id': r.producto_id,
            'producto_nombre': r.producto.nombre,
            'descripcion': r.descripcion,
            'categoria': r.producto.categoria.nombre if r.producto.categoria else 'Sin categoría',
            'cuanto_produce': r.cuanto_produce,
            'tiempo_produccion': r.tiempo_produccion,
            'resistencia': r.resistencia,
            'es_activo': r.es_active == 1,
            'detalles': [{
                'materia_prima_id': d.materia_prima_id,
                'materia_prima_nombre': d.materia_prima.nombre,
                'cantidad': d.cantidad,
                'unidad_id': d.unidad_id,
                'unidad_nombre': d.unidad_medida.nombre
            } for d in r.detalles]
        })

    total_activas = Recetas.query.filter_by(es_active=1).count()
    total_inactivas = Recetas.query.filter_by(es_active=0).count()

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page,
        'activas': total_activas,     
        'inactivas': total_inactivas  
    })

@recetas_bp.route('/recetas/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def guardar_receta():
    data = request.form
    id_receta = data.get('id_receta')

    if not data.get('producto_id') or not data.get('descripcion') or not data.get('cuanto_produce') or not data.get('tiempo_produccion') or not data.get('resistencia'):
        return jsonify({'success': False, 'message': 'Faltan campos obligatorios'}), 400

    detalles_json = data.get('detalles_json')
    if not detalles_json:
        return jsonify({'success': False, 'message': 'Debe agregar al menos un ingrediente'}), 400
    try:
        detalles = json.loads(detalles_json)
    except:
        return jsonify({'success': False, 'message': 'Formato de ingredientes inválido'}), 400

    if not detalles:
        return jsonify({'success': False, 'message': 'Debe agregar al menos un ingrediente'}), 400

    if id_receta:
        receta = Recetas.query.get_or_404(int(id_receta))
        receta.producto_id = int(data['producto_id'])
        receta.descripcion = data['descripcion']
        receta.cuanto_produce = int(data['cuanto_produce'])
        receta.tiempo_produccion = float(data['tiempo_produccion'])
        receta.resistencia = float(data['resistencia'])

        RecetaDetalle.query.filter_by(receta_id=receta.id_receta).delete()

        for d in detalles:
            detalle = RecetaDetalle(
                receta_id=receta.id_receta,
                materia_prima_id=int(d['materia_prima_id']),
                cantidad=float(d['cantidad']),
                unidad_id=int(d['unidad_id'])
            )
            db.session.add(detalle)

        db.session.commit()
        registrar_auditoria(current_user.id, "Editar Receta", f"Receta editada: {receta.descripcion}")
        return jsonify({'success': True, 'message': 'Receta actualizada correctamente.'})
    else:
        receta = Recetas(
            producto_id=int(data['producto_id']),
            descripcion=data['descripcion'],
            cuanto_produce=int(data['cuanto_produce']),
            tiempo_produccion=float(data['tiempo_produccion']),
            resistencia=float(data['resistencia']),
            es_active=1,
            fecha_creacion=datetime.datetime.now()
        )
        db.session.add(receta)
        db.session.flush()  

        for d in detalles:
            detalle = RecetaDetalle(
                receta_id=receta.id_receta,
                materia_prima_id=int(d['materia_prima_id']),
                cantidad=float(d['cantidad']),
                unidad_id=int(d['unidad_id'])
            )
            db.session.add(detalle)

        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Receta", f"Receta creada: {receta.descripcion}")
        return jsonify({'success': True, 'message': 'Receta creada correctamente.'})

@recetas_bp.route('/recetas/obtener/<int:id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def obtener_receta(id):
    receta = Recetas.query.get_or_404(id)
    detalles = [{
        'materia_prima_id': d.materia_prima_id,
        'cantidad': d.cantidad,
        'unidad_id': d.unidad_id
    } for d in receta.detalles]
    return jsonify({
        'id': receta.id_receta,
        'producto_id': receta.producto_id,
        'descripcion': receta.descripcion,
        'cuanto_produce': receta.cuanto_produce,
        'tiempo_produccion': receta.tiempo_produccion,
        'resistencia': receta.resistencia,
        'detalles': detalles
    })

@recetas_bp.route('/recetas/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def alternar_estado(id):
    receta = Recetas.query.get_or_404(id)
    receta.es_active = 0 if receta.es_active == 1 else 1
    estado_txt = "Activada" if receta.es_active == 1 else "Desactivada"
    registrar_auditoria(current_user.id, "Estado Receta", f"Receta {receta.descripcion} {estado_txt}")
    db.session.commit()
    return jsonify({'success': True, 'message': f'Receta {estado_txt.lower()} correctamente.'})

@recetas_bp.route('/recetas/<int:id>')
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def ver_detalle_receta(id):
    receta = Recetas.query.get_or_404(id)
    return render_template('produccion/receta_detalle.html', receta=receta)

@recetas_bp.route('/producto-tiene-receta/<int:producto_id>')
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def producto_tiene_receta(producto_id):
    tiene = Recetas.query.filter_by(producto_id=producto_id, es_active=1).first() is not None
    return jsonify({'tiene_receta': tiene})