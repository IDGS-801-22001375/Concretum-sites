import datetime
import json
from flask import render_template, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from routes.recetas import recetas_bp
from models import db, Recetas, RecetaDetalle, MateriaPrima, UnidadMedida, Productos

def get_productos_opts():
    return [{'value': p.id_producto, 'label': p.nombre} for p in Productos.query.filter_by(es_active=1).all()]

def get_materia_prima_opts():
    return [{'value': mp.id_materia_prima, 'label': mp.nombre} for mp in MateriaPrima.query.filter_by(es_activo=True).all()]

def get_unidades_opts():
    return [{'value': u.id_unidad, 'label': u.nombre} for u in UnidadMedida.query.filter_by(es_active=True).all()]

def registrar_auditoria(usuario_accion, accion, detalles):
    try:
        from app import mongo_db
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Recetas",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

@recetas_bp.route('/recetas', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def get_recetas():
    # KPIs
    total = Recetas.query.count()
    activas = Recetas.query.filter_by(es_active=1).count()
    
    kpis = {
        'total': total,
        'activas': activas
    }

    return render_template(
        'produccion/recetas/recetas.html',
        kpis=kpis,
        productos_options=get_productos_opts(),
        mp_options=get_materia_prima_opts(),
        unidades_options=get_unidades_opts()
    )

@recetas_bp.route('/recetas/api', methods=['GET'])
@login_required
def api_recetas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'descripcion')
    sort_order = request.args.get('sort_order', 'asc')

    query = Recetas.query

    if search:
        query = query.filter(Recetas.descripcion.ilike(f'%{search}%') | Recetas.producto.has(Productos.nombre.ilike(f'%{search}%')))

    if sort_order == 'asc':
        from sqlalchemy import asc
        query = query.order_by(asc(getattr(Recetas, sort_by, Recetas.fecha_creacion)))
    else:
        from sqlalchemy import desc
        query = query.order_by(desc(getattr(Recetas, sort_by, Recetas.fecha_creacion)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for r in paginated.items:
        items.append({
            'id': r.id_receta,
            'producto_nombre': r.producto.nombre if r.producto else 'N/A',
            'categoria': r.producto.categoria.nombre if r.producto and r.producto.categoria else 'N/A',
            'descripcion': r.descripcion,
            'cuanto_produce': r.cuanto_produce,
            'tiempo_produccion': float(r.tiempo_produccion),
            'resistencia': float(r.resistencia),
            'es_activo': r.es_active == 1
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@recetas_bp.route('/recetas/obtener/<int:id>', methods=['GET'])
@login_required
def obtener_receta(id):
    r = Recetas.query.get_or_404(id)
    detalles = [{
        'materia_prima_id': d.materia_prima_id,
        'cantidad': float(d.cantidad),
        'unidad_id': d.unidad_id
    } for d in r.detalles]

    return jsonify({
        'id_receta': r.id_receta,
        'producto_id': r.producto_id,
        'descripcion': r.descripcion,
        'cuanto_produce': r.cuanto_produce,
        'tiempo_produccion': float(r.tiempo_produccion),
        'resistencia': float(r.resistencia),
        'detalles': detalles
    })

@recetas_bp.route('/recetas/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def guardar_receta():
    data = request.form
    id_receta = data.get('id_receta')
    detalles_json = data.get('detalles_json')

    try:
        detalles = json.loads(detalles_json)
    except:
        return jsonify({'success': False, 'message': 'Formato de ingredientes inválido.'}), 400

    if not detalles:
        return jsonify({'success': False, 'message': 'Debe agregar al menos un ingrediente a la receta.'}), 400

    try:
        if id_receta:
            # Editar
            receta = Recetas.query.get_or_404(int(id_receta))
            receta.producto_id = data.get('producto_id')
            receta.descripcion = data.get('descripcion')
            receta.cuanto_produce = data.get('cuanto_produce')
            receta.tiempo_produccion = data.get('tiempo_produccion')
            receta.resistencia = data.get('resistencia')
            receta.fecha_actualizacion = datetime.datetime.now()

            # Eliminar viejos detalles y meter los nuevos
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
            registrar_auditoria(current_user.id, "Editar Receta", f"Receta editada ID: {receta.id_receta}")
            return jsonify({'success': True, 'message': 'Receta actualizada correctamente.'})
        else:
            # Crear
            nueva_receta = Recetas(
                producto_id=data.get('producto_id'),
                descripcion=data.get('descripcion'),
                cuanto_produce=data.get('cuanto_produce'),
                tiempo_produccion=data.get('tiempo_produccion'),
                resistencia=data.get('resistencia'),
                es_active=1,
                fecha_creacion=datetime.datetime.now()
            )
            db.session.add(nueva_receta)
            db.session.flush()

            for d in detalles:
                detalle = RecetaDetalle(
                    receta_id=nueva_receta.id_receta,
                    materia_prima_id=int(d['materia_prima_id']),
                    cantidad=float(d['cantidad']),
                    unidad_id=int(d['unidad_id'])
                )
                db.session.add(detalle)

            db.session.commit()
            registrar_auditoria(current_user.id, "Crear Receta", f"Nueva receta creada ID: {nueva_receta.id_receta}")
            return jsonify({'success': True, 'message': 'Receta registrada correctamente.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

@recetas_bp.route('/recetas/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def alternar_estado(id):
    r = Recetas.query.get_or_404(id)
    r.es_active = 0 if r.es_active == 1 else 1
    estado_txt = "Activada" if r.es_active == 1 else "Desactivada"
    db.session.commit()
    registrar_auditoria(current_user.id, "Estado Receta", f"Receta {estado_txt}: ID {r.id_receta}")
    return jsonify({'success': True, 'message': f'Receta {estado_txt.lower()} correctamente.'})