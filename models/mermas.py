from datetime import datetime
from .extensions import db

class Merma(db.Model):
    __tablename__ = 'mermas'

    id_merma       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    tipo_material  = db.Column(db.Enum('MATERIA_PRIMA', 'PRODUCTO'), nullable=False)
    material_id    = db.Column(db.BigInteger, nullable=False)   # ID de la tabla correspondiente al tipo
    cantidad       = db.Column(db.Numeric(14, 3), nullable=False)
    causa          = db.Column(db.Enum('ROTURA', 'HUMEDAD', 'CADUCIDAD', 'PROCESO', 'TRANSPORTE'), nullable=False)
    responsable    = db.Column(db.String(100))
    observaciones  = db.Column(db.Text)
    valor_monetario = db.Column(db.Numeric(12, 2), nullable=False)
    usuario_id     = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario',                  ondelete='SET NULL'))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    movimiento_id  = db.Column(db.BigInteger, db.ForeignKey('movimientos_inventario.id_movimiento_in', ondelete='SET NULL'))
    produccion_id   = db.Column(db.BigInteger, db.ForeignKey('producciones.id_produccion', ondelete='SET NULL'), nullable=True)

    usuario    = db.relationship('User',                backref='mermas')
    movimiento = db.relationship('MovimientosInventario', backref='merma')
    produccion = db.relationship('Produccion', backref='mermas_imputadas')

    @property
    def id(self):
        return self.id_merma