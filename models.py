from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class categorias_producto(db.Model):
    __tablename__ = 'categorias_producto'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255), nullable=False, unique=True)
    es_active = db.Column(db.BigInteger, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

class productos(db.Model):
    __tablename__ = 'productos'
    
    id_producto = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_producto.id_categoria'), nullable=False, index=True)
    enlace_fotografia = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(100), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.String(255), nullable=False, unique=True)
    unidad_medida = db.Column(db.String(100), nullable=False)
    resistencia_mpa = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(100), nullable=False)
    precio_base = db.Column(db.Float, nullable=False)
    es_active = db.Column(db.BigInteger, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    categoria = db.relationship('categorias_producto', backref='productos')