from datetime import datetime
from .extensions import db

# ====================== COMPRA (cabecera) ======================
class Compra(db.Model):
    __tablename__ = 'compras'

    id_compra      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    proveedor_id   = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor', ondelete='RESTRICT'), nullable=False)
    folio          = db.Column(db.String(40), unique=True, nullable=False)
    fecha_compra   = db.Column(db.DateTime, default=datetime.utcnow)
    total          = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    estado         = db.Column(db.Enum('CREADA', 'RECIBIDA', 'CANCELADA'), default='CREADA')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    pagos = db.relationship('PagoProveedor', backref='compra', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def id(self):
        return self.id_compra


# ====================== COMPRA DETALLE (líneas de la compra) ======================
class CompraDetalle(db.Model):
    __tablename__ = 'compras_detalle'

    id_detalle       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    compra_id        = db.Column(db.BigInteger, db.ForeignKey('compras.id_compra',              ondelete='CASCADE'),   nullable=False)
    materia_prima_id = db.Column(db.BigInteger, db.ForeignKey('materias_primas.id_materia_prima', ondelete='RESTRICT'), nullable=False)
    cantidad         = db.Column(db.Numeric(14, 3), nullable=False)
    precio_unitario  = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal         = db.Column(db.Numeric(12, 2), nullable=False)

    compra        = db.relationship('Compra',      backref='detalles')
    materia_prima = db.relationship('MateriaPrima')

    @property
    def id(self):
        return self.id_detalle


# ====================== HISTORIAL DE COMPRAS (auditoría de estados) ======================
class HistorialCompra(db.Model):
    __tablename__ = 'historial_compras'

    id_historial    = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    compra_id       = db.Column(db.BigInteger, db.ForeignKey('compras.id_compra',    ondelete='CASCADE'),   nullable=False)
    estado_anterior = db.Column(db.Enum('CREADA', 'RECIBIDA', 'CANCELADA'), nullable=True)
    estado_nuevo    = db.Column(db.Enum('CREADA', 'RECIBIDA', 'CANCELADA'), nullable=False)
    usuario_id      = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario',  ondelete='RESTRICT'),  nullable=False)
    observaciones   = db.Column(db.Text)
    fecha_cambio    = db.Column(db.DateTime, default=datetime.utcnow)

    compra  = db.relationship('Compra', backref='historial')
    usuario = db.relationship('User',   backref='cambios_compras')

    @property
    def id(self):
        return self.id_historial