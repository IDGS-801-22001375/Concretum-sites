from datetime import datetime
from .extensions import db

# ====================== CATEGORÍA DE PRODUCTO ======================
class CategoriaProducto(db.Model):
    __tablename__ = 'categorias_producto'

    id_categoria       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre             = db.Column(db.String(120), unique=True, nullable=False)
    descripcion        = db.Column(db.String(255))
    es_activo          = db.Column(db.Boolean, default=True)
    fecha_creacion     = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @property
    def id(self):
        return self.id_categoria


# ====================== PRODUCTO TERMINADO ======================
class Producto(db.Model):
    __tablename__ = 'productos'

    id_producto         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    categoria_id        = db.Column(db.BigInteger, db.ForeignKey('categorias_producto.id_categoria', ondelete='RESTRICT'), nullable=False)
    sku                 = db.Column(db.String(80),  unique=True, nullable=False)
    nombre              = db.Column(db.String(200), nullable=False)
    descripcion         = db.Column(db.String(500))
    unidad_medida       = db.Column(db.Enum('PIEZA', 'M2', 'M3', 'KG', 'TON'), nullable=False)
    resistencia_mpa     = db.Column(db.Numeric(6, 2))
    color               = db.Column(db.String(60))
    precio_base         = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    es_activo           = db.Column(db.Boolean, default=True)
    fecha_creacion      = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

    categoria  = db.relationship('CategoriaProducto', backref='productos')
    existencia = db.relationship(
        'Existencia',
        uselist=False,
        back_populates='producto',
        cascade='all, delete-orphan'
    )

    @property
    def id(self):
        return self.id_producto


# ====================== EXISTENCIA DE PRODUCTO TERMINADO ======================
class Existencia(db.Model):
    __tablename__ = 'existencias'

    id_existencias      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    producto_id         = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='RESTRICT'), unique=True, nullable=False)
    stock_actual        = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    producto     = db.relationship('Producto', back_populates='existencia')
    movimientos  = db.relationship(
        'MovimientoInventario',
        backref='existencia',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def id(self):
        return self.id_existencias