from datetime import datetime
from .extensions import db

# ====================== MOVIMIENTOS DE INVENTARIO ======================
class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'

    id_movimiento_in = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    existencia_id    = db.Column(db.BigInteger, db.ForeignKey('existencias.id_existencias', ondelete='CASCADE'),  nullable=False)
    usuario_id       = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario',        ondelete='SET NULL'), nullable=True)
    tipo             = db.Column(db.Enum('ENTRADA', 'SALIDA', 'AJUSTE'), nullable=False)
    cantidad         = db.Column(db.Numeric(14, 3), nullable=False)
    motivo           = db.Column(db.String(255))
    fecha_creacion   = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('User', backref='movimientos_inventario')

    @property
    def id(self):
        return self.id_movimiento_in