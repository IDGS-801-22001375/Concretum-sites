from datetime import datetime
from .extensions import db

class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'

    id_materia_prima = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sku              = db.Column(db.String(80),  unique=True, nullable=False)
    nombre           = db.Column(db.String(200), nullable=False)
    unidad_medida    = db.Column(db.Enum('KG', 'TON', 'M3', 'LTS'), nullable=False)
    proveedor_id     = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor', ondelete='RESTRICT'), nullable=False)
    stock_minimo     = db.Column(db.Numeric(14, 3), default=0)
    costo_unitario   = db.Column(db.Numeric(12, 2), default=0)
    es_activo        = db.Column(db.Boolean, default=True)
    fecha_creacion   = db.Column(db.DateTime, default=datetime.utcnow)

    proveedor  = db.relationship('Proveedor', backref='materias_primas')
    existencia = db.relationship(
        'ExistenciaMateriaPrima',
        uselist=False,
        back_populates='materia_prima',
        cascade='all, delete-orphan'
    )

    @property
    def id(self):
        return self.id_materia_prima


class ExistenciaMateriaPrima(db.Model):
    __tablename__ = 'existencias_materia_prima'

    id_existencia_mp  = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    materia_prima_id  = db.Column(db.BigInteger, db.ForeignKey('materias_primas.id_materia_prima', ondelete='RESTRICT'), unique=True, nullable=False)
    stock_actual      = db.Column(db.Numeric(14, 3), default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    materia_prima = db.relationship('MateriaPrima', back_populates='existencia')