import enum
from datetime import datetime, timedelta
from .extensions import db

class CategoriaProveedor(enum.Enum):
    MATERIA_PRIMA = "MATERIA_PRIMA"
    SERVICIOS     = "SERVICIOS"
    INSUMOS       = "INSUMOS"

class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    id_proveedor       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    razon_social       = db.Column(db.String(200), nullable=False)
    rfc                = db.Column(db.String(20),  unique=True, nullable=False)
    email              = db.Column(db.String(254), nullable=False)
    telefono           = db.Column(db.String(15),  nullable=False)
    contacto           = db.Column(db.String(100))
    telefono_contacto  = db.Column(db.String(15))
    domicilio          = db.Column(db.Text)
    categoria          = db.Column(db.Enum(CategoriaProveedor), default=CategoriaProveedor.MATERIA_PRIMA)
    dias_credito       = db.Column(db.Integer, default=0)
    limite_credito     = db.Column(db.Numeric(12, 2), default=0)
    es_activo          = db.Column(db.Boolean, default=True)
    fecha_creacion     = db.Column(db.DateTime, default=datetime.utcnow)

    compras = db.relationship('Compra', backref='proveedor', lazy='dynamic')

    @property
    def total_compras(self):
        """Suma total de todas las compras del proveedor."""
        from sqlalchemy import func
        from .compras import Compra
        total = db.session.query(func.sum(Compra.total)).filter(
            Compra.proveedor_id == self.id_proveedor
        ).scalar()
        return float(total or 0)

    @property
    def compras_ultimo_mes(self):
        from sqlalchemy import func
        from .compras import Compra
        ultimo_mes = datetime.utcnow() - timedelta(days=30)
        total = db.session.query(func.sum(Compra.total)).filter(
            Compra.proveedor_id == self.id_proveedor,
            Compra.fecha_compra >= ultimo_mes
        ).scalar()
        return float(total or 0)

    @property
    def cuentas_vencidas(self):
        from .pagos import PagoProveedor
        hoy = datetime.utcnow().date()
        return PagoProveedor.query.filter(
            PagoProveedor.compra.has(proveedor_id=self.id_proveedor),
            PagoProveedor.fecha_vencimiento < hoy,
            PagoProveedor.fecha_pago == None
        ).all()

    @property
    def monto_vencido(self):
        return sum(p.monto for p in self.cuentas_vencidas)

    @property
    def id(self):
        return self.id_proveedor