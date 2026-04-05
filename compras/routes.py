from flask import render_template, request, jsonify, session
from flask_security import login_required, roles_accepted, current_user
from models import db, Compra, CompraDetalle, HistorialCompra, Proveedor, MateriaPrima, ExistenciaMateriaPrima
from . import compras_bp
from sqlalchemy import or_, asc, desc, func
import datetime
import uuid

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Compras",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

# ----------------------------------------------------------------------
# VISTA PRINCIPAL
# ----------------------------------------------------------------------
@compras_bp.route('/compras')
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS', 'COMPRADOR')
def index():
    total_ordenes = Compra.query.count()
    pendientes = Compra.query.filter(Compra.estado == 'CREADA').count()
    recibidas = Compra.query.filter(Compra.estado == 'RECIBIDA').count()
    canceladas = Compra.query.filter(Compra.estado == 'CANCELADA').count()
    
    proveedores = Proveedor.query.filter_by(es_activo=True).all()
    proveedores_options = [{'value': p.id, 'label': p.razon_social} for p in proveedores]
    
    materias = MateriaPrima.query.filter_by(es_activo=True).all()
    materias_options = [{'value': m.id, 'label': f"{m.sku} - {m.nombre}"} for m in materias]
    
    kpis = {
        'total_ordenes': total_ordenes,
        'pendientes': pendientes,
        'recibidas': recibidas,
        'canceladas': canceladas
    }
    return render_template('compras/index.html', 
                           kpis=kpis,
                           proveedores_options=proveedores_options,
                           materias_options=materias_options)

# ----------------------------------------------------------------------
# API LISTAR COMPRAS
# ----------------------------------------------------------------------
@compras_bp.route('/compras/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS', 'COMPRADOR')
def api_compras():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'fecha_compra')
    sort_order = request.args.get('sort_order', 'desc')
    search = request.args.get('search', '')
    estado_filter = request.args.get('estado', '')
    proveedor_filter = request.args.get('proveedor', '')

    query = Compra.query
    if search:
        query = query.filter(or_(
            Compra.folio.ilike(f'%{search}%'),
            Compra.proveedor.has(Proveedor.razon_social.ilike(f'%{search}%'))
        ))
    if estado_filter:
        query = query.filter(Compra.estado == estado_filter)
    if proveedor_filter:
        query = query.filter(Compra.proveedor_id == int(proveedor_filter))

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Compra, sort_by, Compra.fecha_compra)))
    else:
        query = query.order_by(desc(getattr(Compra, sort_by, Compra.fecha_compra)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for c in paginated.items:
        items.append({
            'id': c.id,
            'folio': c.folio,
            'proveedor_id': c.proveedor_id,
            'proveedor_nombre': c.proveedor.razon_social,
            'fecha_compra': c.fecha_compra.strftime('%Y-%m-%d %H:%M'),
            'total': float(c.total),
            'estado': c.estado,
            'es_activo': True
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

# ----------------------------------------------------------------------
# OBTENER COMPRA
# ----------------------------------------------------------------------
@compras_bp.route('/compras/obtener/<int:id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS')
def obtener_compra(id):
    compra = Compra.query.get_or_404(id)
    detalles = [{
        'materia_prima_id': d.materia_prima_id,
        'materia_prima_nombre': d.materia_prima.nombre,
        'cantidad': float(d.cantidad),
        'precio_unitario': float(d.precio_unitario),
        'subtotal': float(d.subtotal)
    } for d in compra.detalles]
    return jsonify({
        'id': compra.id,
        'folio': compra.folio,
        'proveedor_id': compra.proveedor_id,
        'fecha_compra': compra.fecha_compra.strftime('%Y-%m-%dT%H:%M'),
        'total': float(compra.total),
        'estado': compra.estado,
        'detalles': detalles
    })

# ----------------------------------------------------------------------
# GUARDAR COMPRA (CREAR O EDITAR)
# ----------------------------------------------------------------------
@compras_bp.route('/compras/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS')
def guardar_compra():
    data = request.form
    id_compra = data.get('id_compra')
    
    # Validar fecha
    fecha_str = data.get('fecha_compra')
    if not fecha_str:
        return jsonify({'success': False, 'errors': {'fecha_compra': 'La fecha y hora son obligatorias.'}}), 400
    try:
        fecha_compra = datetime.datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'success': False, 'errors': {'fecha_compra': 'Formato de fecha inválido.'}}), 400
    
    # Validar detalles
    detalles_json = data.get('detalles_json')
    if not detalles_json:
        return jsonify({'success': False, 'errors': {'general': 'Debe agregar al menos un material.'}}), 400
    
    import json
    try:
        detalles = json.loads(detalles_json)
    except:
        return jsonify({'success': False, 'errors': {'general': 'Formato de detalles inválido.'}}), 400
    
    if not detalles:
        return jsonify({'success': False, 'errors': {'general': 'Debe agregar al menos un material.'}}), 400
    
    total = sum(float(d['cantidad']) * float(d['precio_unitario']) for d in detalles)
    
    if id_compra:
        # Editar (solo si está CREADA)
        compra = Compra.query.get_or_404(int(id_compra))
        if compra.estado != 'CREADA':
            return jsonify({'success': False, 'errors': {'general': 'No se puede editar una compra ya recibida o cancelada.'}}), 400
        
        compra.proveedor_id = int(data['proveedor_id'])
        compra.fecha_compra = fecha_compra
        compra.total = total
        # Eliminar detalles antiguos y crear nuevos
        CompraDetalle.query.filter_by(compra_id=compra.id).delete()
        for d in detalles:
            detalle = CompraDetalle(
                compra_id=compra.id,
                materia_prima_id=int(d['materia_prima_id']),
                cantidad=float(d['cantidad']),
                precio_unitario=float(d['precio_unitario']),
                subtotal=float(d['cantidad']) * float(d['precio_unitario'])
            )
            db.session.add(detalle)
        db.session.commit()
        registrar_auditoria(current_user.id, "Editar Compra", f"Compra editada: {compra.folio}")
        return jsonify({'success': True, 'message': 'Compra actualizada correctamente.'})
    else:
        # Crear nueva
        folio = f"OC-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        compra = Compra(
            proveedor_id=int(data['proveedor_id']),
            folio=folio,
            fecha_compra=fecha_compra,
            total=total,
            estado='CREADA'
        )
        db.session.add(compra)
        db.session.flush()
        
        for d in detalles:
            detalle = CompraDetalle(
                compra_id=compra.id,
                materia_prima_id=int(d['materia_prima_id']),
                cantidad=float(d['cantidad']),
                precio_unitario=float(d['precio_unitario']),
                subtotal=float(d['cantidad']) * float(d['precio_unitario'])
            )
            db.session.add(detalle)
        
        historial = HistorialCompra(
            compra_id=compra.id,
            estado_anterior=None,
            estado_nuevo='CREADA',
            usuario_id=current_user.id,
            observaciones='Compra creada'
        )
        db.session.add(historial)
        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Compra", f"Compra creada: {compra.folio}")
        return jsonify({'success': True, 'message': f'Compra creada con folio {folio}.'})

# ----------------------------------------------------------------------
# CAMBIAR ESTADO (CON ACTUALIZACIÓN DE STOCK AL RECIBIR Y AL CANCELAR)
# ----------------------------------------------------------------------
@compras_bp.route('/compras/cambiar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS')
def cambiar_estado(id):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    observaciones = data.get('observaciones', '')
    
    compra = Compra.query.get_or_404(id)
    estado_anterior = compra.estado
    
    # Validaciones
    if estado_anterior == 'CANCELADA':
        return jsonify({'success': False, 'message': 'No se puede cambiar el estado de una compra cancelada.'}), 400
    if estado_anterior == 'RECIBIDA' and nuevo_estado != 'CANCELADA':
        return jsonify({'success': False, 'message': 'Una compra recibida solo puede ser cancelada.'}), 400
    if nuevo_estado not in ['RECIBIDA', 'CANCELADA']:
        return jsonify({'success': False, 'message': 'Estado inválido.'}), 400
    
    try:
        if nuevo_estado == 'RECIBIDA':
            # Sumar stock
            for detalle in compra.detalles:
                existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=detalle.materia_prima_id).first()
                if not existencia:
                    existencia = ExistenciaMateriaPrima(materia_prima_id=detalle.materia_prima_id, stock_actual=0)
                    db.session.add(existencia)
                    db.session.flush()
                existencia.stock_actual += detalle.cantidad
            compra.estado = 'RECIBIDA'
        elif nuevo_estado == 'CANCELADA' and estado_anterior == 'RECIBIDA':
            # Restar stock (revertir la recepción)
            for detalle in compra.detalles:
                existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=detalle.materia_prima_id).first()
                if existencia:
                    existencia.stock_actual -= detalle.cantidad
                    # Evitar stock negativo
                    if existencia.stock_actual < 0:
                        existencia.stock_actual = 0
            compra.estado = 'CANCELADA'
        else:
            compra.estado = nuevo_estado
        
        # Registrar historial
        historial = HistorialCompra(
            compra_id=compra.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            usuario_id=current_user.id,
            observaciones=observaciones
        )
        db.session.add(historial)
        db.session.commit()
        
        registrar_auditoria(current_user.id, "Cambio Estado Compra", 
                            f"Compra {compra.folio}: {estado_anterior} → {nuevo_estado}")
        return jsonify({'success': True, 'message': f'Estado cambiado a {nuevo_estado} correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ----------------------------------------------------------------------
# ELIMINAR COMPRA (solo CREADA)
# ----------------------------------------------------------------------
@compras_bp.route('/compras/eliminar/<int:id>', methods=['DELETE'])
@login_required
@roles_accepted('ADMINISTRADOR')
def eliminar_compra(id):
    compra = Compra.query.get_or_404(id)
    if compra.estado != 'CREADA':
        return jsonify({'success': False, 'message': 'Solo se pueden eliminar compras en estado CREADA.'}), 400
    db.session.delete(compra)
    db.session.commit()
    registrar_auditoria(current_user.id, "Eliminar Compra", f"Compra {compra.folio} eliminada.")
    return jsonify({'success': True, 'message': 'Compra eliminada correctamente.'})