from routes.inventario import inventario_bp
from flask import render_template, request
from models import db, Existencias, Productos

def obtener_productos(page=1):
    pagination = db.session.query(Existencias)\
        .join(Productos, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .paginate(page=page, per_page=5)

    inactivos_count = db.session.query(Productos)\
        .filter(Productos.es_active == 0)\
        .count()

    return pagination, pagination.items, inactivos_count

@inventario_bp.route('/inventario')
def get_inventario():
    page = request.args.get('page', 1, type=int)

    return render_template('produccion/inventario/inventario.html')