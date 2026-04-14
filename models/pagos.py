from datetime import datetime
from .extensions import db

class PagoProveedor(db.Model):
    __tablename__ = 'pagos_proveedor'

    id_pago          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    compra_id        = db.Column(db.BigInteger, db.ForeignKey('compras.id_compra', ondelete='RESTRICT'), nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    fecha_pago       = db.Column(db.Date, nullable=True)
    monto            = db.Column(db.Numeric(12, 2), nullable=False)
    forma_pago       = db.Column(db.Enum('EFECTIVO', 'TRANSFERENCIA', 'CHEQUE'), default='TRANSFERENCIA')
    estatus          = db.Column(db.Enum('PENDIENTE', 'PAGADO', 'VENCIDO'), default='PENDIENTE')
    observaciones    = db.Column(db.Text)
    fecha_creacion   = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def id(self):
        return self.id_pago