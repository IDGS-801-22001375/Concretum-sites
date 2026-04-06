from routes.produccion.productos import productos_bp
from .forms import ProductoForm
from flask import render_template, request, redirect, url_for, flash, session
from .models import UnidadMedida, Color, categorias_producto, productos
from extensions import db

### Funciones ###

def get_colores():
    return [(c.id_color, c.nombre) for c in Color.query.filter_by(es_active=True).all()]

def get_unidades():
    return [(u.id_unidad, u.nombre) for u in UnidadMedida.query.filter_by(es_active=True).all()]

def get_categorias():
    return [(ca.id_categoria, ca.nombre) for ca in categorias_producto.query.filter_by(es_active=True).all()]

@productos_bp.route('/productos')
def get_datos():
    form = ProductoForm(request.form)

    page = request.args.get('page', 1, type=int)

    pagination = db.session.query(productos)\
        .join(categorias_producto, productos.categoria_id == categorias_producto.id_categoria)\
        .filter(productos.es_active == 1)\
        .paginate(page=page, per_page=5)

    productos_lista = pagination.items

    return render_template('produccion/productos/productos.html', form=form, productos=productos_lista, pagination=pagination)