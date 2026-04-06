from datetime import datetime
from .extensions import db

# ====================== RECETA ======================
class Receta(db.Model):
    __tablename__ = 'recetas'

    id_receta      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    producto_id    = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), nullable=False)
    descripcion    = db.Column(db.String(255))
    cuanto_produce = db.Column(db.Numeric(14, 3), nullable=False)
    es_activa      = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto', backref='recetas')

    @property
    def id(self):
        return self.id_receta


# ====================== PRODUCCIÓN ======================
class Produccion(db.Model):
    __tablename__ = 'producciones'

    id_produccion     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    producto_id       = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    receta_id         = db.Column(db.BigInteger, db.ForeignKey('recetas.id_receta',     ondelete='RESTRICT'), nullable=False)
    cantidad_producida = db.Column(db.Numeric(14, 3), nullable=False)
    unidad_medida     = db.Column(db.Enum('PIEZA', 'M2', 'M3', 'KG', 'TON'), nullable=False)
    fecha_inicio      = db.Column(db.DateTime, nullable=False)
    fecha_fin         = db.Column(db.DateTime, nullable=True)
    estado            = db.Column(
        db.Enum('PLANIFICADA', 'EN_PROCESO', 'FINALIZADA', 'CANCELADA'),
        nullable=False,
        default='PLANIFICADA'
    )
    observaciones  = db.Column(db.String(500))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto', backref='producciones')
    receta   = db.relationship('Receta',   backref='producciones')

    @property
    def id(self):
        return self.id_produccion