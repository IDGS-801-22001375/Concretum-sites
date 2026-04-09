import datetime
from flask_login import login_required
from flask_security.decorators import roles_accepted
from werkzeug.datastructures import CombinedMultiDict
from routes.productos import productos_bp
from forms import ProductoForm
from flask import render_template, request, redirect, url_for, flash
from models import UnidadMedida, Color, CategoriasProducto, db, Productos, Existencias
import uuid
import os
from werkzeug.utils import secure_filename

### Funciones GET ###

def get_colores():
    return [(c.id_color, c.nombre) for c in Color.query.filter_by(es_active=True).all()]

def get_unidades():
    return [(u.id_unidad, u.nombre) for u in UnidadMedida.query.filter_by(es_active=True).all()]

def get_categorias():
    return [(ca.id_categoria, ca.nombre) for ca in CategoriasProducto.query.filter_by(es_active=True).all()]

def obtener_productos(page=1):
    pagination = db.session.query(Productos)\
        .join(CategoriasProducto, Productos.categoria_id == CategoriasProducto.id_categoria)\
        .join(Existencias, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .paginate(page=page, per_page=5)

    inactivos_count = db.session.query(Productos)\
        .filter(Productos.es_active == 0)\
        .count()
        
    todas = db.session.query(Existencias)\
        .join(Productos, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .all()

    bajo_stock = sum(1 for e in todas if e.estado_stock == 'BAJO')

    return pagination, pagination.items, inactivos_count, bajo_stock

def convertir_ruta_imagen(enlace_fotografia):
    filename = secure_filename(enlace_fotografia.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"

    ruta_relativa = f"images/productos/{unique_name}"
    ruta_fisica = os.path.join("static", ruta_relativa)

    enlace_fotografia.save(ruta_fisica)

    return ruta_relativa

######################

# ── GET ──────────────────────────────────────────────────────────────────────

@productos_bp.route('/productos')
@login_required
@roles_accepted("ADMINISTRADOR", "ADMIN", "SUPER_ADMIN")
def get_datos():
    form = ProductoForm(request.form)

    form.categoria_id.choices = get_categorias()
    form.unidad_medida.choices = get_unidades()
    form.color.choices = get_colores()

    page = request.args.get('page', 1, type=int)
    form_activo = request.args.get('modo') == 'nuevo'

    pagination, productos_lista, inactivos_count, bajo_stock = obtener_productos(page)

    return render_template(
        'produccion/productos/productos.html',
        form=form,
        productos=productos_lista,
        pagination=pagination,
        inactivos_count=inactivos_count,
        modo_edicion=False,
        form_activo=form_activo,
        id_producto=None,
        bajo_stock=bajo_stock
    )

# ── GUARDAR ──────────────────────────────────────────────────────────────────

@login_required
@roles_accepted("ADMINISTRADOR", "ADMIN", "SUPER_ADMIN")
@productos_bp.route('/productos', methods=['POST'])
def save_producto():

    form = ProductoForm(CombinedMultiDict([request.form, request.files]))

    form.categoria_id.choices = get_categorias()
    form.unidad_medida.choices = get_unidades()
    form.color.choices = get_colores()

    if not form.validate_on_submit():
        flash("Formulario inválido", "danger")
        return redirect(url_for('productos_bp.get_datos'))

    enlace_fotografia = form.enlace_fotografia.data

    filename = convertir_ruta_imagen(enlace_fotografia)
    if not filename:
        flash("La imagen no pudo ser procesada", "danger")
        return redirect(url_for('productos_bp.get_datos'))

    producto_data = {
        "categoria_id": form.categoria_id.data,
        "enlace_fotografia": filename,
        "sku": form.sku.data,
        "nombre": form.nombre.data,
        "descripcion": form.descripcion.data,
        "unidad_medida_id": form.unidad_medida.data,
        "resistencia_mpa": form.resistencia_mpa.data,
        "color_id": form.color.data,
        "precio_base": form.precio_base.data,
        "fecha_creacion": form.fecha_creacion.data or datetime.datetime.now()
    }

    try:
        nuevo_producto = Productos(**producto_data)
        db.session.add(nuevo_producto)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Error al guardar el producto", "danger")
        return redirect(url_for('productos_bp.get_datos'))

    flash("Producto guardado correctamente", "success")
    return redirect(url_for('productos_bp.get_datos'))

# ── EDITAR ───────────────────────────────────────────────────────────────────

@productos_bp.route("/productos/<int:id_producto>", methods=['GET', 'POST'])
@login_required
@roles_accepted("ADMINISTRADOR", "ADMIN", "SUPER_ADMIN")
def update_producto(id_producto):

    producto = db.session.query(Productos).filter_by(id_producto=id_producto).first()

    if not producto:
        return render_template("404.html"), 404

    form = ProductoForm(obj=producto)

    form.categoria_id.choices = get_categorias()
    form.unidad_medida.choices = get_unidades()
    form.color.choices = get_colores()

    if form.validate_on_submit():
        producto.categoria_id = form.categoria_id.data
        producto.sku = form.sku.data
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.unidad_medida_id = form.unidad_medida.data
        producto.resistencia_mpa = form.resistencia_mpa.data
        producto.color_id = form.color.data
        producto.precio_base = form.precio_base.data

        if form.enlace_fotografia.data:
            filename = convertir_ruta_imagen(form.enlace_fotografia.data)
            producto.enlace_fotografia = filename

        db.session.commit()
        flash("Producto actualizado correctamente", "success")

        return redirect(url_for('productos_bp.get_datos'))

    page = request.args.get('page', 1, type=int)
    pagination, productos_lista, inactivos_count, bajo_stock = obtener_productos(page)

    return render_template(
        "produccion/productos/productos.html",
        form=form,
        productos=productos_lista,
        pagination=pagination,
        inactivos_count=inactivos_count,
        form_activo=True,
        modo_edicion=True, 
        id_producto=id_producto,
        bajo_stock=bajo_stock
    )

# ── ELIMINAR ───────────────────────────────────────────────────

@productos_bp.route("/productos/<int:id_producto>/eliminar", methods=['POST'])
@login_required
@roles_accepted("ADMINISTRADOR", "ADMIN", "SUPER_ADMIN")
def delete_producto(id_producto):

    producto = db.session.query(Productos).filter_by(id_producto=id_producto).first()

    if not producto:
        return render_template("404.html"), 404

    producto.es_active = 0
    db.session.commit()

    flash("Producto eliminado correctamente", "warning")
    return redirect(url_for('productos_bp.get_datos'))