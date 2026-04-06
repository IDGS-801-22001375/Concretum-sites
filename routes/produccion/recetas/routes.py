import datetime
from sqlalchemy.orm import joinedload
from flask import flash, redirect, render_template, request, url_for

from routes.produccion.recetas import recetas_bp
from routes.produccion.recetas.forms import RecetaForm, RecetaDetalleForm
from routes.produccion.recetas.models import Recetas, RecetaDetalle, MateriaPrima, db
from routes.produccion.productos.models import UnidadMedida, Productos


def get_producto():
    return [(p.id_producto, p.nombre) for p in Productos.query.filter_by(es_active=True).all()]

def get_materia_prima():
    return [(mp.id_materia_prima, mp.nombre) for mp in MateriaPrima.query.filter_by(es_active=True).all()]

def get_unidades():
    return [(u.id_unidad, u.nombre) for u in UnidadMedida.query.filter_by(es_active=True).all()]

def _poblar_choices(form):
    form.producto_id.choices = get_producto()
    materias = get_materia_prima()
    unidades = get_unidades()
    
    for entry in form.ingredientes:
        entry.materia_prima_id.choices = materias
        entry.unidad_id.choices = unidades

def obtener_datos_recetas(page=1):
    pagination = (
        db.session.query(Recetas)
        .options(joinedload(Recetas.producto), joinedload(Recetas.detalles))
        .filter(Recetas.es_active == 1)
        .paginate(page=page, per_page=3)
    )
    return pagination, pagination.items

def _render(form, page=1, **kwargs):
    pagination, recetas_lista = obtener_datos_recetas(page)
    return render_template(
        'produccion/recetas/recetas.html',
        form=form,
        recetas=recetas_lista,
        pagination=pagination,
        today=datetime.date.today().isoformat(),
        **kwargs
    )

# ── GET ──────────────────────────────────────────────────────────────────────

@recetas_bp.route('/recetas', methods=['GET'])
def get_recetas():
    form = RecetaForm()
    _poblar_choices(form)
    page = request.args.get('page', 1, type=int)
    form_activo = request.args.get('modo') == 'nuevo'
    
    return _render(form, page=page, modo_edicion=False, form_activo=form_activo)


# ── GUARDAR ──────────────────────────────────────────────────────────────────

@recetas_bp.route('/recetas', methods=['POST'])
def save_receta():
    form = RecetaForm(request.form)
    page = request.args.get('page', 1, type=int)

    if 'agregar_ingrediente' in request.form:
        form.ingredientes.append_entry()
        _poblar_choices(form)
        return _render(form, page=page, modo_edicion=False, form_activo=True)

    if 'quitar_ingrediente' in request.form:
        idx = int(request.form['quitar_ingrediente'])
        if len(form.ingredientes.entries) > 1:
            form.ingredientes.entries.pop(idx)
        _poblar_choices(form)
        return _render(form, page=page, modo_edicion=False, form_activo=True)

    _poblar_choices(form)
    if not form.validate():
        flash("Revisa los errores del formulario", "danger")
        return _render(form, page=page, modo_edicion=False, form_activo=True)

    try:
        nueva_receta = Recetas(
            producto_id=form.producto_id.data,
            descripcion=form.descripcion.data,
            cuanto_produce=form.cuanto_produce.data,
            tiempo_produccion=form.tiempo_produccion.data,
            resistencia=form.resistencia.data,
            fecha_creacion=form.fecha_creacion.data,
        )
        db.session.add(nueva_receta)
        db.session.flush()

        for entrada in form.ingredientes:
            detalle = RecetaDetalle(
                receta_id=nueva_receta.id_receta,
                materia_prima_id=entrada.materia_prima_id.data,
                cantidad=entrada.cantidad.data,
                unidad_id=entrada.unidad_id.data,
            )
            db.session.add(detalle)

        db.session.commit()
        flash("Receta guardada correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar la receta: {str(e)}", "danger")

    return redirect(url_for('recetas_bp.get_recetas'))


# ── EDITAR ───────────────────────────────────────────────────────────────────

@recetas_bp.route('/recetas/<int:id_receta>/editar', methods=['GET', 'POST'])
def editar_receta(id_receta):
    receta = Recetas.query.filter_by(id_receta=id_receta, es_active=1).first_or_404()
    page = request.args.get('page', 1, type=int)

    if request.method == 'GET':
        form = RecetaForm(obj=receta)

        while form.ingredientes.entries:
            form.ingredientes.pop_entry()

        for det in receta.detalles:
            form.ingredientes.append_entry({
                'materia_prima_id': det.materia_prima_id,
                'cantidad': det.cantidad,
                'unidad_id': det.unidad_id,
            })

        _poblar_choices(form)
        return _render(form, page=page, modo_edicion=True, form_activo=True, receta_editando=receta)

    form = RecetaForm(request.form)

    if 'agregar_ingrediente' in request.form:
        form.ingredientes.append_entry()
        _poblar_choices(form)
        return _render(form, page=page, modo_edicion=True, form_activo=True, receta_editando=receta)

    if 'quitar_ingrediente' in request.form:
        idx = int(request.form['quitar_ingrediente'])
        if len(form.ingredientes.entries) > 1:
            form.ingredientes.entries.pop(idx)
        _poblar_choices(form)
        return _render(form, page=page, modo_edicion=True, form_activo=True, receta_editando=receta)

    _poblar_choices(form)
    if not form.validate():
        flash("Revisa los errores del formulario", "danger")
        return _render(form, page=page, modo_edicion=True, form_activo=True, receta_editando=receta)

    try:
        receta.producto_id = form.producto_id.data
        receta.descripcion = form.descripcion.data
        receta.cuanto_produce = form.cuanto_produce.data
        receta.tiempo_produccion = form.tiempo_produccion.data
        receta.resistencia = form.resistencia.data
        receta.fecha_actualizacion = datetime.datetime.now()

        RecetaDetalle.query.filter_by(receta_id=receta.id_receta).delete()

        for entrada in form.ingredientes:
            detalle = RecetaDetalle(
                receta_id=receta.id_receta,
                materia_prima_id=entrada.materia_prima_id.data,
                cantidad=entrada.cantidad.data,
                unidad_id=entrada.unidad_id.data,
            )
            db.session.add(detalle)

        db.session.commit()
        flash("Receta actualizada correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar la receta: {str(e)}", "danger")

    return redirect(url_for('recetas_bp.get_recetas'))


# ── ELIMINAR ───────────────────────────────────────────────────

@recetas_bp.route('/recetas/<int:id_receta>/eliminar', methods=['POST'])
def eliminar_receta(id_receta):
    receta = Recetas.query.filter_by(id_receta=id_receta, es_active=1).first_or_404()

    try:
        receta.es_active = 0
        receta.fecha_actualizacion = datetime.datetime.now()
        db.session.commit()
        flash("Receta eliminada correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la receta: {str(e)}", "danger")

    return redirect(url_for('recetas_bp.get_recetas'))  