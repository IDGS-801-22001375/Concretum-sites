from flask import Flask, render_template
from config import DevelopmentConfig
from routes.produccion.productos import productos_bp
from routes.administracion.proveedores import proveedores_bp
from routes.produccion.inventario import inventario_bp
from routes.produccion.recetas import recetas_bp
from routes.produccion.productos.models import Productos, CategoriasProducto
from extensions import db
from config import DevelopmentConfig
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SECRET_KEY'] = 'npTi0yksIMIvBhG0rTj6k1'
csrf = CSRFProtect(app)
db.init_app(app)

app.register_blueprint(productos_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(recetas_bp)

@app.route("/")
@app.route("/index")
def index():
    productos_lista = db.session.query(Productos)\
        .join(CategoriasProducto, Productos.categoria_id == CategoriasProducto.id_categoria)\
        .filter(Productos.es_active == 1)\
        .order_by(Productos.fecha_creacion.desc())\
        .limit(6)\
        .all()
    return render_template("/home/index.html", productos_lista=productos_lista)

@app.route("/admin")
def admin():
    return render_template("/layout-admin.html")

if __name__ == '__main__':
	app.run(debug=True)