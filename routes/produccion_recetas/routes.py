from flask import render_template, redirect, url_for, flash
from datetime import datetime
import threading
import time

from models.inventario_produccion import Existencias
from routes.produccion_recetas import produccion_recetas_bp

from models import db
from models import Produccion, ProduccionConsumo
from models import Recetas, RecetaDetalle
from models import MateriaPrima

from forms import ProduccionForm

def convertir_unidades(cantidad, origen, destino):
    if origen == destino:
        return float(cantidad)

    conversion = {
        ('KG', 'TON'): lambda x: x / 1000,
        ('TON', 'KG'): lambda x: x * 1000,
    }

    return conversion.get((origen, destino), lambda x: x)(float(cantidad))


def finalizar_produccion(id_produccion):
    time.sleep(300)

    produccion = Produccion.query.get(id_produccion)

    if produccion and produccion.estado == 'EN_PROCESO':
        produccion.estado = 'FINALIZADA'
        produccion.fecha_fin = datetime.utcnow()
        db.session.commit()


# ====================== INDEX ======================

@produccion_recetas_bp.route('/producciones')
def index():
    historial = Produccion.query.order_by(Produccion.id_produccion.desc()).all()

    recetas = Recetas.query.filter_by(es_active=1).all()

    ordenes_activas_list = Produccion.query.filter(
        Produccion.estado == 'EN_PROCESO'
    ).all()

    form = ProduccionForm()
    
    form.receta_id.choices = [
        (r.id_receta, f"{r.descripcion} - {r.producto.nombre}")
        for r in recetas
    ]

    return render_template(
        'produccion/pedidos_produccion/pedidos-produccion.html',
        historial=historial,
        recetas=recetas,
        ordenes_activas_list=ordenes_activas_list,
        form=form
    )


# ====================== CREAR ======================

@produccion_recetas_bp.route('/crear', methods=['POST'])
def crear_orden():
    form = ProduccionForm()

    if not form.validate_on_submit():
        flash('Formulario inválido', 'error')
        return redirect(url_for('produccion_recetas_bp.index'))

    receta = Recetas.query.get(form.receta_id.data)
    cantidad = form.cantidad.data

    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()

    consumos = []

    for det in detalles:
        mp = MateriaPrima.query.get(det.materia_prima_id)
        existencia = mp.existencia

        if not existencia:
            flash(f"No hay existencia para {mp.nombre}", 'error')
            return redirect(url_for('produccion_recetas_bp.index'))

        cantidad_necesaria = det.cantidad * cantidad

        cantidad_convertida = convertir_unidades(
            cantidad_necesaria,
            'KG',
            mp.unidad_medida
        )

        if float(existencia.stock_actual) < cantidad_convertida:
            flash(f"Stock insuficiente de {mp.nombre}", 'error')
            return redirect(url_for('produccion_recetas_bp.index'))

        consumos.append((mp, existencia, cantidad_convertida))

    produccion = Produccion(
        producto_id=receta.producto_id,
        receta_id=receta.id_receta,
        cantidad_producida=cantidad,
        unidad_medida='PIEZA',
        fecha_inicio=form.fecha_inicio.data,
        estado='EN_PROCESO',
        observaciones=form.observaciones.data
    )

    db.session.add(produccion)
    db.session.flush()

    for mp, existencia, cantidad in consumos:
        existencia.stock_actual = float(existencia.stock_actual) - cantidad

        db.session.add(ProduccionConsumo(
            produccion_id=produccion.id_produccion,
            materia_prima_id=mp.id_materia_prima,
            cantidad_usada=cantidad
        ))

    db.session.commit()

    threading.Thread(
        target=finalizar_produccion,
        args=(produccion.id_produccion,)
    ).start()

    flash('Producción iniciada', 'success')
    return redirect(url_for('produccion_recetas_bp.index'))


# ====================== CANCELAR ======================

@produccion_recetas_bp.route('/cancelar/<int:id>', methods=['POST'])
def cancelar_orden(id):
    produccion = Produccion.query.get_or_404(id)

    if produccion.estado != 'EN_PROCESO':
        flash('Solo puedes cancelar producciones en proceso', 'error')
        return redirect(url_for('produccion_recetas_bp.index'))

    consumos = ProduccionConsumo.query.filter_by(
        produccion_id=id
    ).all()

    for c in consumos:
        mp = MateriaPrima.query.get(c.materia_prima_id)
        mp.existencia.stock_actual += float(c.cantidad_usada)

    produccion.estado = 'CANCELADA'
    db.session.commit()

    flash('Producción cancelada', 'warning')
    return redirect(url_for('produccion_recetas_bp.index'))


# ====================== FINALIZAR ======================

@produccion_recetas_bp.route('/finalizar/<int:id>', methods=['POST'])
def finalizar_manual(id):
    produccion = Produccion.query.get_or_404(id)

    if produccion.estado != 'EN_PROCESO':
        flash('Solo puedes finalizar producciones en proceso', 'error')
        return redirect(url_for('produccion_recetas_bp.index'))

    produccion.estado = 'FINALIZADA'
    produccion.fecha_fin = datetime.utcnow()
    
    existencia = Existencias.query.filter_by(producto_id=produccion.producto_id).first()

    cantidad_final = produccion.cantidad_producida * produccion.receta.cuanto_produce

    existencia.stock_actual += cantidad_final

    db.session.commit()

    flash('Producción finalizada', 'success')
    return redirect(url_for('produccion_recetas_bp.index'))