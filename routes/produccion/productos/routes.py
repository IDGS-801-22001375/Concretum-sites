from routes.produccion.productos import productos_bp
from .forms import ProductoForm
from flask import render_template, request, redirect, url_for, flash, session
from .models import UnidadMedida, Color

### Funciones ###

def get_colores():
    return [(c.id, c.nombre) for c in Color.query.filter_by(activo=True).all()]

def get_unidades():
    return [(u.id, u.nombre) for u in UnidadMedida.query.filter_by(activo=True).all()]

@productos_bp.route('/productos')
def get_datos():
    form = ProductoForm(request.form)

    form.color.choices = get_colores()
    form.unidad_medida.choices = get_unidades()

    return render_template('productos.html', form=form)