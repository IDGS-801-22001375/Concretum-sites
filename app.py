from flask import Flask, render_template
from config import DevelopmentConfig
from routes.productos import productos_bp
from models import db, productos, categorias_producto
from config import DevelopmentConfig
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect(app)
db.init_app(app)

app.register_blueprint(productos_bp)

@app.route("/")
@app.route("/index")
def index():
    productos_lista = db.session.query(productos)\
        .join(categorias_producto, productos.categoria_id == categorias_producto.id_categoria)\
        .filter(productos.es_active == 1)\
        .order_by(productos.fecha_creacion.desc())\
        .limit(6)\
        .all()
    return render_template("/home/index.html", productos_lista=productos_lista)

@app.route("/admin")
def admin():
    return render_template("/layout-admin.html")

if __name__ == '__main__':
	app.run(debug=True)
 