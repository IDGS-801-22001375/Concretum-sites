from datetime import datetime
from .extensions import db

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
    pedido_id = db.Column(db.BigInteger, db.ForeignKey('pedidos_cliente.id_pedido_cliente', ondelete='SET NULL'), nullable=True)
    solicitud_id = db.Column(db.BigInteger, db.ForeignKey('solicitudes_produccion.id_solicitud', ondelete='SET NULL'), nullable=True)

    producto = db.relationship('Productos', backref='producciones')
    receta   = db.relationship('Recetas',   backref='producciones')
    pedido = db.relationship('PedidoCliente', backref='producciones')
    solicitud = db.relationship('SolicitudProduccion', backref='produccion')

    @property
    def id(self):
        return self.id_produccion
    
# ====================== PRODUCCIÓN CONSUMO ======================
class ProduccionConsumo(db.Model):
    __tablename__ = 'produccion_consumo'

    id_consumo       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    produccion_id    = db.Column(
        db.BigInteger,
        db.ForeignKey('producciones.id_produccion', ondelete='CASCADE'),
        nullable=False
    )
    materia_prima_id = db.Column(
        db.BigInteger,
        db.ForeignKey('materias_primas.id_materia_prima', ondelete='RESTRICT'),
        nullable=False
    )
    cantidad_usada   = db.Column(db.Numeric(14, 3), nullable=False)
    fecha_registro   = db.Column(db.DateTime, default=datetime.utcnow)

    produccion     = db.relationship('Produccion', backref='consumos')
    materia_prima  = db.relationship('MateriaPrima', backref='consumos')

    @property
    def id(self):
        return self.id_consumo
    
# ====================== LOTES DE PRODUCCIÓN ======================
class LoteProduccion(db.Model):
    __tablename__ = 'lotes_produccion'

    id_lote         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    produccion_id   = db.Column(
        db.BigInteger,
        db.ForeignKey('producciones.id_produccion', ondelete='CASCADE'),
        nullable=False
    )
    codigo_lote     = db.Column(db.String(50), nullable=False, unique=True)
    fecha_fabricacion = db.Column(db.Date, nullable=False)

    produccion = db.relationship('Produccion', backref='lotes')

    @property
    def id(self):
        return self.id_lote