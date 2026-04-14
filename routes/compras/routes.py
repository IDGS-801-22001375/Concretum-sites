from flask import render_template, request, jsonify, session
from flask_security import login_required, roles_accepted, current_user
from models import db, Compra, CompraDetalle, HistorialCompra, Proveedor, MateriaPrima, ExistenciaMateriaPrima
from . import compras_bp
from sqlalchemy import or_, asc, desc, func
import datetime
import uuid
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
        "modulo": "Compras",
        "user_agent": user_agent,
        "ip": ip_addr,
        "fecha_creacion": datetime.datetime.utcnow()
    }
    
    threading.Thread(target=_guardar_en_mongo, args=(datos_auditoria,)).start()

@compras_bp.route('/compras')
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
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

@compras_bp.route('/compras/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
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
        productos_resumen = []
        for det in c.detalles[:3]:
            mp = det.materia_prima
            productos_resumen.append(f"{mp.nombre} x {float(det.cantidad)} {mp.unidad_medida}")
        if len(c.detalles) > 3:
            productos_resumen.append(f"+{len(c.detalles)-3} más")
        resumen_str = ", ".join(productos_resumen) if productos_resumen else "Sin materiales"
        
        items.append({
            'id': c.id,
            'folio': c.folio,
            'proveedor_nombre': c.proveedor.razon_social,
            'fecha_compra': c.fecha_compra.strftime('%Y-%m-%d %H:%M'), 
            'total': float(c.total),
            'estado': c.estado,
            'productos_resumen': resumen_str
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@compras_bp.route('/compras/obtener/<int:id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
def obtener_compra(id):
    compra = Compra.query.get_or_404(id)
    detalles = [{
        'materia_prima_id': d.materia_prima_id,
        'materia_prima_nombre': d.materia_prima.nombre,
        'cantidad': float(d.cantidad),
        'precio_unitario': float(d.precio_unitario),
        'subtotal': float(d.total_linea)
    } for d in compra.detalles]
    return jsonify({
        'id': compra.id,
        'folio': compra.folio,
        'proveedor_id': compra.proveedor_id,
        'fecha_compra': compra.fecha_compra.strftime('%Y-%m-%d'), 
        'total': float(compra.total),
        'estado': compra.estado,
        'detalles': detalles
    })

@compras_bp.route('/compras/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
def guardar_compra():
    data = request.form
    id_compra = data.get('id_compra')
    
    fecha_str = data.get('fecha_compra')
    if not fecha_str:
        return jsonify({'success': False, 'errors': {'fecha_compra': 'La fecha es obligatoria.'}}), 400
    try:
        fecha_compra = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
        fecha_compra = fecha_compra.replace(hour=23, minute=59, second=59)
    except ValueError:
        return jsonify({'success': False, 'errors': {'fecha_compra': 'Formato de fecha inválido.'}}), 400
    
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
        compra = Compra.query.get_or_404(int(id_compra))
        if compra.estado != 'CREADA':
            return jsonify({'success': False, 'errors': {'general': 'No se puede editar una compra ya recibida o cancelada.'}}), 400
        
        compra.proveedor_id = int(data['proveedor_id'])
        compra.fecha_compra = fecha_compra
        compra.total = total
        CompraDetalle.query.filter_by(compra_id=compra.id).delete()
        for d in detalles:
            detalle = CompraDetalle(
                compra_id=compra.id,
                materia_prima_id=int(d['materia_prima_id']),
                cantidad=float(d['cantidad']),
                precio_unitario=float(d['precio_unitario']),
                total_linea=float(d['cantidad']) * float(d['precio_unitario'])
            )
            db.session.add(detalle)
        db.session.commit()
        registrar_auditoria(current_user.id, "Editar Compra", f"Compra editada: {compra.folio}")
        return jsonify({'success': True, 'message': 'Compra actualizada correctamente.'})
    else:
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
                total_linea=float(d['cantidad']) * float(d['precio_unitario']) 
            )
            db.session.add(detalle)
        
        historial = HistorialCompra(
            compra_id=compra.id,
            accion='CREADA',
            modificado_por=current_user.id,
            comentario='Compra generada automáticamente.'
        )

        db.session.add(historial)
        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Compra", f"Compra creada: {compra.folio}")
        return jsonify({'success': True, 'message': f'Compra creada con folio {folio}.'})

@compras_bp.route('/compras/cambiar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
def cambiar_estado(id):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    observaciones = data.get('observaciones', '')
    
    compra = Compra.query.get_or_404(id)
    estado_anterior = compra.estado
    
    if estado_anterior == 'CANCELADA':
        return jsonify({'success': False, 'message': 'No se puede cambiar el estado de una compra cancelada.'}), 400
    if estado_anterior == 'RECIBIDA' and nuevo_estado != 'CANCELADA':
        return jsonify({'success': False, 'message': 'Una compra recibida solo puede ser cancelada.'}), 400
    if nuevo_estado not in ['RECIBIDA', 'CANCELADA']:
        return jsonify({'success': False, 'message': 'Estado inválido.'}), 400
    
    try:
        if nuevo_estado == 'RECIBIDA':
            for detalle in compra.detalles:
                existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=detalle.materia_prima_id).first()
                if not existencia:
                    existencia = ExistenciaMateriaPrima(materia_prima_id=detalle.materia_prima_id, stock_actual=0)
                    db.session.add(existencia)
                    db.session.flush()
                existencia.stock_actual += detalle.cantidad
            compra.estado = 'RECIBIDA'
        elif nuevo_estado == 'CANCELADA' and estado_anterior == 'RECIBIDA':
            for detalle in compra.detalles:
                existencia = ExistenciaMateriaPrima.query.filter_by(materia_prima_id=detalle.materia_prima_id).first()
                if existencia:
                    existencia.stock_actual -= detalle.cantidad
                    if existencia.stock_actual < 0:
                        existencia.stock_actual = 0
            compra.estado = 'CANCELADA'
        else:
            compra.estado = nuevo_estado
        
        historial = HistorialCompra(
            compra_id=compra.id,
            accion='ACTUALIZADA' if nuevo_estado != 'CREADA' else 'CREADA', 
            modificado_por=current_user.id,
            comentario=f"Cambio de estado: {estado_anterior} -> {nuevo_estado}. {observaciones}"
        )
        db.session.add(historial)
        db.session.commit()
        
        registrar_auditoria(current_user.id, "Cambio Estado Compra", 
                            f"Compra {compra.folio}: {estado_anterior} → {nuevo_estado}")
        return jsonify({'success': True, 'message': f'Estado cambiado a {nuevo_estado} correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@compras_bp.route('/compras/eliminar/<int:id>', methods=['DELETE'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
def eliminar_compra(id):
    compra = Compra.query.get_or_404(id)
    if compra.estado != 'CREADA':
        return jsonify({'success': False, 'message': 'Solo se pueden eliminar compras en estado CREADA.'}), 400
    db.session.delete(compra)
    db.session.commit()
    registrar_auditoria(current_user.id, "Eliminar Compra", f"Compra {compra.folio} eliminada.")
    return jsonify({'success': True, 'message': 'Compra eliminada correctamente.'})


@compras_bp.route('/compras/api/materiales/<int:proveedor_id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
def materiales_proveedor(proveedor_id):
    materias = MateriaPrima.query.filter_by(proveedor_id=proveedor_id, es_activo=True).all()
    
    data = [{'id': m.id_materia_prima, 'nombre': f"{m.sku} - {m.nombre}", 'unidad': m.unidad_medida} for m in materias]
    return jsonify(data)


@compras_bp.route('/compras/generar_automatica', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS', 'PRODUCCION') 
def generar_compra_automatica():
    data = request.get_json()
    mp_id = data.get('materia_prima_id')
    cantidad = float(data.get('cantidad', 0))

    mp = MateriaPrima.query.get_or_404(mp_id)

    if not mp.proveedor_id:
        return jsonify({'success': False, 'message': f'El material {mp.nombre} no tiene un proveedor asignado.'}), 400

    costo_unitario = float(mp.costo_unitario) if mp.costo_unitario else 0
    total = cantidad * costo_unitario

    folio = f"OC-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    try:
        compra = Compra(
            proveedor_id=mp.proveedor_id,
            folio=folio,
            fecha_compra=datetime.datetime.now(),
            total=total,
            estado='CREADA'
        )
        db.session.add(compra)
        db.session.flush()

        detalle = CompraDetalle(
            compra_id=compra.id,
            materia_prima_id=mp.id,
            cantidad=cantidad,
            precio_unitario=costo_unitario,
            total_linea=total
        )
        db.session.add(detalle)

        historial = HistorialCompra(
            compra_id=compra.id,
            accion='CREADA',
            modificado_por=current_user.id,
            comentario='Generada automáticamente desde solicitud de producción.'
        )
        db.session.add(historial)
        db.session.commit()

        registrar_auditoria(current_user.id, "Compra Automática", f"OC {folio} generada por falta de stock.")

        return jsonify({'success': True, 'message': f'Orden {folio} generada con éxito.'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al generar la compra: {str(e)}'}), 500
    
@compras_bp.route('/compras/detalle/<int:id>')
@login_required
@roles_accepted('ADMINISTRADOR', 'COMPRAS')
def detalle_compra(id):
    from sqlalchemy.orm import joinedload
    compra = Compra.query.options(
        joinedload(Compra.detalles).joinedload(CompraDetalle.materia_prima),
        joinedload(Compra.historial).joinedload(HistorialCompra.usuario)
    ).get_or_404(id)
    
    total_pagado = sum(p.monto for p in compra.pagos if p.estatus == 'PAGADO')
    saldo_pendiente = compra.total - total_pagado
    
    return render_template('compras/detalle.html',
                           compra=compra,
                           total_pagado=total_pagado,
                           saldo_pendiente=saldo_pendiente)