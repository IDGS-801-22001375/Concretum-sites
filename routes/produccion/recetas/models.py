import datetime
from extensions import db

class Recetas(db.Model):
    __tablename__ = 'recetas'
    
    id_receta = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False, index=True)
    descripcion = db.Column(db.String(255), nullable=False, unique=True)
    cuanto_produce = db.Column(db.Integer, nullable=False)
    tiempo_produccion = db.Column(db.Float, nullable=False)
    resistencia = db.Column(db.Float, nullable=False)
    es_active = db.Column(db.BigInteger, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    producto = db.relationship('Productos', backref='recetas')
    
class RecetaDetalle(db.Model):
    __tablename__ = 'receta_detalle'
    
    id_detalle = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id_receta'), nullable=False, index=True)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia_prima'), nullable=False, index=True)
    cantidad = db.Column(db.Integer, nullable=False)
    unidad_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id_unidad'), nullable=False, index=True)
 
    receta = db.relationship('Recetas', backref='detalles')
    unidad_medida = db.relationship('UnidadMedida', backref='recetas_detalle')
    materia_prima = db.relationship('MateriaPrima', backref='recetas_detalle')    
    
class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'

    id_materia_prima = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    unidad_medida = db.Column(db.Integer, db.ForeignKey('UnidadMedida.id_unidad'), nullable=False, index=True)
    es_active = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    existencia = db.relationship('ExistenciaMateriaPrima', back_populates='materia_prima', uselist=False, cascade="all, delete-orphan")
    
class ExistenciaMateriaPrima(db.Model):
    __tablename__ = 'existencias_materia_prima'
    
    id_existencia_mp = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    materia_prima_id = db.Column(db.BigInteger, db.ForeignKey('materias_primas.id_materia_prima'), nullable=False, unique=True)
    stock_actual = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    materia_prima = db.relationship('MateriaPrima', back_populates='existencia')