from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from datetime import datetime
from models.inventario_produccion import Existencias
from routes.produccion_recetas import produccion_recetas_bp
from models import (
    db, Produccion, ProduccionConsumo, Recetas, RecetaDetalle, MateriaPrima,
    SolicitudProduccion, PedidoCliente, PedidoClienteDetalle,
    NotificacionCliente, MovimientosInventario, Productos, UnidadMedida
)
from routes.carrito.routes import _crear_notificacion
from sqlalchemy import desc, asc

import threading
import time
import math

def convertir_unidades(cantidad, origen, destino):
    if origen == destino:
        return float(cantidad)
    
    conversion = {
        ('KG', 'TON'): lambda x: x / 1000.0,
        ('TON', 'KG'): lambda x: x * 1000.0,
        ('LTS', 'M3'): lambda x: x / 1000.0,
        ('M3', 'LTS'): lambda x: x * 1000.0,
    }
    
    func_conversion = conversion.get((origen, destino))
    if func_conversion:
        return func_conversion(float(cantidad))
    
    return float(cantidad)

def finalizar_produccion(id_produccion):
    # Simulador de tiempo de producción en background (30 seg para pruebas)
    time.sleep(30)
    with db.app.app_context():
        produccion = Produccion.query.get(id_produccion)
        if produccion and produccion.estado == 'EN_PROCESO':
            produccion.estado = 'FINALIZADA'
            produccion.fecha_fin = datetime.utcnow()
            db.session.commit()

# ====================== VISTA PRINCIPAL ======================

@produccion_recetas_bp.route('/producciones')
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def index():
    recetas = Recetas.query.filter_by(es_active=1).all()
    recetas_opts = [
        {'value': r.id_receta, 'label': f"{r.descripcion} - {r.producto.nombre}"} 
        for r in recetas
    ]
    return render_template(
        'produccion/pedidos_produccion/pedidos-produccion.html',
        recetas_options=recetas_opts
    )

# ====================== APIS PARA AJAX ======================

@produccion_recetas_bp.route('/api/kpis_y_activas')
@login_required
def api_kpis_y_activas():
    activas = Produccion.query.filter_by(estado='EN_PROCESO').all()
    finalizadas = Produccion.query.filter_by(estado='FINALIZADA').count()
    canceladas = Produccion.query.filter_by(estado='CANCELADA').count()
    total = Produccion.query.count()

    ordenes_activas = [{
        'id': o.id_produccion,
        'producto': o.producto.nombre,
        'cantidad': float(o.cantidad_producida)
    } for o in activas]

    return jsonify({
        'kpis': {
            'activas': len(activas),
            'finalizadas': finalizadas,
            'canceladas': canceladas,
            'total': total
        },
        'ordenes_activas': ordenes_activas
    })

@produccion_recetas_bp.route('/historial/api')
@login_required
def api_historial():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = Produccion.query

    if search:
        query = query.filter(Produccion.producto.has(Productos.nombre.ilike(f'%{search}%')))

    query = query.order_by(desc(Produccion.id_produccion))
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for o in paginated.items:
        items.append({
            'id_produccion': f"#{o.id_produccion}",
            'producto_nombre': o.producto.nombre,
            'cantidad_producida': float(o.cantidad_producida),
            'estado': o.estado,
            'fecha_inicio': o.fecha_inicio.strftime('%d/%m/%Y %H:%M') if o.fecha_inicio else ''
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

# ====================== ACCIONES (CREAR, FINALIZAR, CANCELAR) ======================

@produccion_recetas_bp.route('/crear', methods=['POST'])
@login_required
def crear_orden():
    data = request.form
    receta_id = data.get('receta_id')
    cantidad = float(data.get('cantidad', 0))
    fecha_inicio = data.get('fecha_inicio')
    observaciones = data.get('observaciones', '')

    if not receta_id or cantidad <= 0 or not fecha_inicio:
        return jsonify({'success': False, 'message': 'Datos inválidos.'}), 400

    receta = Recetas.query.get_or_404(int(receta_id))
    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    consumos = []

    # Validar stock antes de crear
    for det in detalles:
        mp = MateriaPrima.query.get(det.materia_prima_id)
        existencia = mp.existencia

        if not existencia:
            return jsonify({'success': False, 'message': f"No hay registro de inventario para {mp.nombre}"}), 400

        unidad_origen = UnidadMedida.query.get(det.unidad_id).clave
        
        cantidad_necesaria = det.cantidad * cantidad
        cantidad_convertida = convertir_unidades(cantidad_necesaria, unidad_origen, mp.unidad_medida)

        if float(existencia.stock_actual) < cantidad_convertida:
            return jsonify({'success': False, 'message': f"Stock insuficiente de {mp.nombre}. Necesitas {cantidad_convertida:.2f}, tienes {existencia.stock_actual:.2f}"}), 400

        consumos.append((mp, existencia, cantidad_convertida))

    try:
        # Crear producción
        produccion = Produccion(
            producto_id=receta.producto_id,
            receta_id=receta.id_receta,
            cantidad_producida=cantidad,
            unidad_medida='PIEZA',
            fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d'),
            estado='EN_PROCESO',
            observaciones=observaciones
        )
        db.session.add(produccion)
        db.session.flush()

        # Descontar stock y registrar consumos
        for mp, existencia, cant_conv in consumos:
            existencia.stock_actual = float(existencia.stock_actual) - cant_conv
            db.session.add(ProduccionConsumo(
                produccion_id=produccion.id_produccion,
                materia_prima_id=mp.id_materia_prima,
                cantidad_usada=cant_conv
            ))

        db.session.commit()

        # Iniciar simulación en background
        threading.Thread(target=finalizar_produccion, args=(produccion.id_produccion,)).start()

        return jsonify({'success': True, 'message': 'Orden de producción iniciada correctamente.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@produccion_recetas_bp.route('/finalizar/<int:id>', methods=['POST'])
@login_required
def finalizar_manual(id):
    from decimal import Decimal
    produccion = Produccion.query.get_or_404(id)
    
    if produccion.estado != 'EN_PROCESO':
        return jsonify({'success': False, 'message': 'Solo puedes finalizar producciones en proceso.'}), 400

    existencia = Existencias.query.filter_by(producto_id=produccion.producto_id).first()
    if not existencia:
        return jsonify({'success': False, 'message': 'Error: El producto no tiene registro de inventario.'}), 400

    try:
        cantidad_producida_dec = Decimal(str(produccion.cantidad_producida))
        cuanto_produce_dec = Decimal(str(produccion.receta.cuanto_produce))
        cantidad_final = cantidad_producida_dec * cuanto_produce_dec
        
        existencia.stock_actual += cantidad_final

        movimiento = MovimientosInventario(
            existencia_id=existencia.id_existencias,
            usuario_id=current_user.id,
            tipo='ENTRADA',
            cantidad=cantidad_final,
            motivo=f'Producción finalizada ID {produccion.id_produccion}'
        )
        db.session.add(movimiento)

        produccion.estado = 'FINALIZADA'
        produccion.fecha_fin = datetime.utcnow()

        # Actualizar la solicitud de producción asociada (si existe)
        if produccion.solicitud_id:
            solicitud = SolicitudProduccion.query.get(produccion.solicitud_id)
            if solicitud:
                solicitud.estado = 'COMPLETADA'
                solicitud.fecha_respuesta = datetime.utcnow()

                # Actualizar el pedido: reducir cantidad pendiente
                pedido = solicitud.pedido
                if pedido:
                    detalle = PedidoClienteDetalle.query.filter_by(
                        pedido_id=pedido.id_pedido_cliente,
                        producto_id=produccion.producto_id
                    ).first()
                    if detalle and detalle.cantidad_pendiente > 0:
                        entregar = min(detalle.cantidad_pendiente, cantidad_final)
                        detalle.cantidad_entregada += entregar
                        detalle.cantidad_pendiente -= entregar

                        if all(d.cantidad_pendiente == 0 for d in pedido.detalles):
                            pedido.estado = 'ENTREGADO'
                        else:
                            pedido.estado = 'PARCIALMENTE_ENTREGADO'

                    _crear_notificacion(
                        usuario_id=pedido.usuario_id,
                        tipo='ENTREGA',
                        titulo=f'Producto listo - {pedido.folio}',
                        mensaje=f'El producto {produccion.producto.nombre} ya está disponible para entrega.',
                        referencia_id=pedido.id_pedido_cliente,
                        referencia_tipo='pedido_cliente',
                    )

        db.session.commit()
        return jsonify({'success': True, 'message': 'Producción finalizada y stock sumado al almacén.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@produccion_recetas_bp.route('/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar_orden(id):
    produccion = Produccion.query.get_or_404(id)
    if produccion.estado != 'EN_PROCESO':
        return jsonify({'success': False, 'message': 'Solo puedes cancelar producciones en proceso.'}), 400

    try:
        consumos = ProduccionConsumo.query.filter_by(produccion_id=id).all()
        for c in consumos:
            mp = MateriaPrima.query.get(c.materia_prima_id)
            mp.existencia.stock_actual += float(c.cantidad_usada)

        produccion.estado = 'CANCELADA'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Producción cancelada y materiales devueltos al stock.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ====================== RUTAS SOLICITUDES INTACTAS ======================

@produccion_recetas_bp.route('/solicitudes')
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def solicitudes_pendientes():
    """Lista de solicitudes de producción pendientes (estado PENDIENTE)"""
    solicitudes = SolicitudProduccion.query.filter_by(estado='PENDIENTE').order_by(SolicitudProduccion.fecha_solicitud.asc()).all()
    return render_template('produccion/solicitudes.html', solicitudes=solicitudes)

@produccion_recetas_bp.route('/solicitudes/<int:solicitud_id>/aceptar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def aceptar_solicitud(solicitud_id):
    """Acepta una solicitud, calcula lotes, descuenta stock y crea una orden de producción"""
    solicitud = SolicitudProduccion.query.get_or_404(solicitud_id)
    if solicitud.estado != 'PENDIENTE':
        flash('Esta solicitud ya fue procesada.', 'warning')
        return redirect(url_for('produccion_recetas_bp.solicitudes_pendientes'))

    receta = Recetas.query.filter_by(producto_id=solicitud.producto_id, es_active=1).first()
    if not receta:
        flash(f'No hay receta activa para el producto {solicitud.producto.nombre}', 'danger')
        return redirect(url_for('produccion_recetas_bp.solicitudes_pendientes'))

    lotes_necesarios = math.ceil(float(solicitud.cantidad_faltante) / float(receta.cuanto_produce))

    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    consumos = []

    for det in detalles:
        mp = MateriaPrima.query.get(det.materia_prima_id)
        existencia = mp.existencia
        if not existencia:
            flash(f"No hay registro de inventario para {mp.nombre}", 'danger')
            return redirect(url_for('produccion_recetas_bp.solicitudes_pendientes'))

        unidad_origen = UnidadMedida.query.get(det.unidad_id).clave
        cantidad_necesaria = float(det.cantidad) * lotes_necesarios
        cantidad_convertida = convertir_unidades(cantidad_necesaria, unidad_origen, mp.unidad_medida)

        if float(existencia.stock_actual) < cantidad_convertida:
            flash(f"Stock insuficiente de {mp.nombre} para fabricar los lotes automáticos. Necesitas {cantidad_convertida:.2f} {mp.unidad_medida}, tienes {existencia.stock_actual:.2f}", 'danger')
            return redirect(url_for('produccion_recetas_bp.solicitudes_pendientes'))

        consumos.append((mp, existencia, cantidad_convertida))

    try:
        produccion = Produccion(
            producto_id=solicitud.producto_id,
            receta_id=receta.id_receta,
            cantidad_producida=lotes_necesarios,
            unidad_medida='PIEZA',
            fecha_inicio=datetime.utcnow(),
            estado='EN_PROCESO',
            observaciones=f'Producción por solicitud #{solicitud.id_solicitud} (Cubre {solicitud.cantidad_faltante} uds solicitadas)',
            pedido_id=solicitud.pedido_id,
            solicitud_id=solicitud.id_solicitud
        )
        db.session.add(produccion)
        db.session.flush()

        for mp, existencia, cant_conv in consumos:
            existencia.stock_actual = float(existencia.stock_actual) - cant_conv
            db.session.add(ProduccionConsumo(
                produccion_id=produccion.id_produccion,
                materia_prima_id=mp.id_materia_prima,
                cantidad_usada=cant_conv
            ))

        solicitud.estado = 'ACEPTADA'
        solicitud.fecha_respuesta = datetime.utcnow()
        db.session.commit()

        threading.Thread(target=finalizar_produccion, args=(produccion.id_produccion,)).start()

        pedido = solicitud.pedido
        if pedido:
            _crear_notificacion(
                usuario_id=pedido.usuario_id,
                tipo='PRODUCCION',
                titulo=f'Producción iniciada - {pedido.folio}',
                mensaje=f'La producción del producto {solicitud.producto.nombre} ha iniciado para cubrir tu pedido.',
                referencia_id=solicitud.id_solicitud,
                referencia_tipo='solicitud_produccion'
            )

        flash(f'Solicitud #{solicitud.id_solicitud} aceptada. Se descontó la materia prima y se inició la producción #{produccion.id_produccion}.', 'success')
        return redirect(url_for('produccion_recetas_bp.solicitudes_pendientes'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
        return redirect(url_for('produccion_recetas_bp.solicitudes_pendientes'))