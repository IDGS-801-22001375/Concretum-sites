import datetime
from .extensions import db

class CategoriasProducto(db.Model):
    __tablename__ = 'categorias_producto'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255), nullable=False, unique=True)
    es_active = db.Column(db.BigInteger, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

class Productos(db.Model):
    __tablename__ = 'productos'
    
    id_producto = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_producto.id_categoria'), nullable=False, index=True)
    enlace_fotografia = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(100), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.String(255), nullable=False, unique=True)
    unidad_medida_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id_unidad'))    
    resistencia_mpa = db.Column(db.Float, nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('colores.id_color'))
    precio_base = db.Column(db.Float, nullable=False)
    es_active = db.Column(db.BigInteger, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    categoria = db.relationship('CategoriasProducto', backref='productos')
    unidad_medida = db.relationship('UnidadMedida', backref='productos')
    color = db.relationship('Color', backref='productos')

class Color(db.Model):
    __tablename__ = 'colores'

    id_color = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    codigo_hex = db.Column(db.String(7))
    es_active = db.Column(db.Boolean, default=True)

class UnidadMedida(db.Model):
    __tablename__ = 'unidades_medida'

    id_unidad = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    es_active = db.Column(db.Boolean, default=True)