from datetime import datetime
from .extensions import db

# ====================== CONFIGURACIÓN DE EMPRESA ======================
class ConfiguracionEmpresa(db.Model):
    __tablename__ = 'configuracion_empresa'

    id                       = db.Column(db.BigInteger, primary_key=True)
    razon_social             = db.Column(db.String(200), nullable=False, default='Mi Empresa')
    rfc                      = db.Column(db.String(20),  nullable=False, unique=True, default='XAXX010101000')
    direccion                = db.Column(db.Text, default='')
    telefono                 = db.Column(db.String(20), default='')
    email_facturacion        = db.Column(db.String(254), default='')
    logo                     = db.Column(db.String(255), nullable=True)   # ruta del archivo

    # Alertas
    alerta_stock_minimo      = db.Column(db.Boolean, default=True)
    alerta_vencimiento_credito = db.Column(db.Boolean, default=True)
    alerta_merma_diaria      = db.Column(db.Boolean, default=False)

    # Preferencias
    moneda                   = db.Column(db.String(3),  default='MXN')
    zona_horaria             = db.Column(db.String(50), default='America/Mexico_City')
    actualizado_por          = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'))
    fecha_actualizacion      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantiza un único registro en la tabla
        if not self.id and ConfiguracionEmpresa.query.count() == 0:
            db.session.add(self)
            db.session.commit()