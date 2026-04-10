import datetime
from .extensions import db

class Existencias(db.Model):
    __tablename__ = 'existencias'

    id_existencias = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False, unique=True)
    stock_actual = db.Column(db.Numeric(14, 3), nullable=False, default=0.000)
    stock_minimo = db.Column(db.Numeric(14, 3), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    estado_stock = db.Column(db.Enum('BAJO','PRECAUCION', 'ALTO'), nullable=False, default='ALTO')

    producto = db.relationship('Productos', backref=db.backref('existencia', uselist=False))
    
class MovimientosInventario(db.Model):
    __tablename__ = 'movimientos_inventario'

    id_movimiento_in = db.Column(db.Integer, primary_key=True)
    existencia_id = db.Column(db.Integer, db.ForeignKey('existencias.id_existencias'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True, index=True)
    tipo = db.Column(db.Enum('ENTRADA', 'SALIDA', 'AJUSTE'), nullable=False)
    cantidad = db.Column(db.Numeric(14, 3), nullable=False)
    motivo = db.Column(db.String(255), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)

    existencia = db.relationship('Existencias', backref='movimientos')
    usuario = db.relationship('User', backref='movimientos_inventario')

    @property
    def id(self):
        return self.id_movimiento_in