import datetime
from .extensions import db


# ============================================================
# CARRITO
# ============================================================

class Carrito(db.Model):
    __tablename__ = 'carritos'

    id_carrito          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    usuario_id          = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False, unique=True)
    fecha_creacion      = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    usuario = db.relationship('User', backref=db.backref('carrito', uselist=False))
    items   = db.relationship('CarritoItem', backref='carrito', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def id(self):
        return self.id_carrito

    @property
    def total_items(self):
        return sum(int(item.cantidad) for item in self.items)

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items)


class CarritoItem(db.Model):
    __tablename__ = 'carrito_items'

    id_item         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    carrito_id      = db.Column(db.BigInteger, db.ForeignKey('carritos.id_carrito', ondelete='CASCADE'), nullable=False)
    producto_id     = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad        = db.Column(db.Numeric(14, 3), nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_agregado  = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    producto = db.relationship('Productos', backref='carrito_items')

    @property
    def id(self):
        return self.id_item

    @property
    def subtotal(self):
        return float(self.cantidad) * float(self.precio_unitario)


# ============================================================
# PEDIDOS CLIENTE
# ============================================================

class PedidoCliente(db.Model):
    __tablename__ = 'pedidos_cliente'

    id_pedido_cliente   = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    folio               = db.Column(db.String(40), nullable=False, unique=True)
    usuario_id          = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario', ondelete='RESTRICT'), nullable=False)
    metodo_pago         = db.Column(db.Enum('TARJETA', 'TRANSFERENCIA', 'OXXO'), nullable=False, default='TARJETA')
    estado              = db.Column(
        db.Enum('PENDIENTE', 'PAGADO', 'EN_PRODUCCION', 'ENVIADO', 'ENTREGADO', 'CANCELADO'),
        nullable=False, default='PENDIENTE'
    )
    subtotal            = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    iva                 = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total               = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    direccion_entrega   = db.Column(db.String(500))
    notas               = db.Column(db.Text)
    fecha_pedido        = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    usuario  = db.relationship('User', backref='pedidos_cliente')
    detalles = db.relationship('PedidoClienteDetalle', backref='pedido', cascade='all, delete-orphan')

    @property
    def id(self):
        return self.id_pedido_cliente

    ETIQUETAS_ESTADO = {
        'PENDIENTE':     'Pendiente de pago',
        'PAGADO':        'Pago confirmado',
        'EN_PRODUCCION': 'En producción',
        'ENVIADO':       'Enviado',
        'ENTREGADO':     'Entregado',
        'CANCELADO':     'Cancelado',
    }

    @property
    def etiqueta_estado(self):
        return self.ETIQUETAS_ESTADO.get(self.estado, self.estado)


class PedidoClienteDetalle(db.Model):
    __tablename__ = 'pedidos_cliente_detalle'

    id_detalle      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    pedido_id       = db.Column(db.BigInteger, db.ForeignKey('pedidos_cliente.id_pedido_cliente', ondelete='CASCADE'), nullable=False)
    producto_id     = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad        = db.Column(db.Numeric(14, 3), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    total_linea     = db.Column(db.Numeric(12, 2), nullable=False)
    stock_suficiente = db.Column(db.SmallInteger, nullable=False, default=1)

    producto = db.relationship('Productos')

    @property
    def id(self):
        return self.id_detalle


# ============================================================
# SOLICITUDES DE PRODUCCIÓN URGENTE
# ============================================================

class SolicitudProduccion(db.Model):
    __tablename__ = 'solicitudes_produccion'

    id_solicitud      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    pedido_id         = db.Column(db.BigInteger, db.ForeignKey('pedidos_cliente.id_pedido_cliente', ondelete='CASCADE'), nullable=False)
    producto_id       = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad_faltante = db.Column(db.Numeric(14, 3), nullable=False)
    estado            = db.Column(
        db.Enum('PENDIENTE', 'ACEPTADA', 'RECHAZADA', 'EN_PROCESO', 'COMPLETADA'),
        nullable=False, default='PENDIENTE'
    )
    observaciones   = db.Column(db.Text)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_respuesta = db.Column(db.DateTime)

    pedido   = db.relationship('PedidoCliente', backref='solicitudes_produccion')
    producto = db.relationship('Productos', backref='solicitudes_produccion')

    @property
    def id(self):
        return self.id_solicitud


# ============================================================
# NOTIFICACIONES CLIENTE
# ============================================================

class NotificacionCliente(db.Model):
    __tablename__ = 'notificaciones_cliente'

    id_notificacion = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    usuario_id      = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    tipo            = db.Column(db.Enum('INFO', 'PRODUCCION', 'STOCK', 'PAGO', 'ENTREGA'), nullable=False, default='INFO')
    titulo          = db.Column(db.String(200), nullable=False)
    mensaje         = db.Column(db.Text, nullable=False)
    leida           = db.Column(db.SmallInteger, nullable=False, default=0)
    referencia_id   = db.Column(db.BigInteger)
    referencia_tipo = db.Column(db.String(50))
    fecha_creacion  = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    usuario = db.relationship('User', backref='notificaciones')

    @property
    def id(self):
        return self.id_notificacion


# ============================================================
# COTIZACIONES
# ============================================================

class Cotizacion(db.Model):
    __tablename__ = 'cotizaciones'

    id_cotizacion       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    folio               = db.Column(db.String(40), nullable=False, unique=True)
    usuario_id          = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario', ondelete='RESTRICT'), nullable=False)
    estado              = db.Column(
        db.Enum('BORRADOR', 'ENVIADA', 'ACEPTADA', 'RECHAZADA', 'EXPIRADA'),
        nullable=False, default='BORRADOR'
    )
    subtotal            = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    iva                 = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total               = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    notas               = db.Column(db.Text)
    fecha_expiracion    = db.Column(db.Date)
    fecha_creacion      = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    usuario  = db.relationship('User', backref='cotizaciones')
    detalles = db.relationship('CotizacionDetalle', backref='cotizacion', cascade='all, delete-orphan')

    @property
    def id(self):
        return self.id_cotizacion


class CotizacionDetalle(db.Model):
    __tablename__ = 'cotizaciones_detalle'

    id_detalle      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    cotizacion_id   = db.Column(db.BigInteger, db.ForeignKey('cotizaciones.id_cotizacion', ondelete='CASCADE'), nullable=False)
    producto_id     = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad        = db.Column(db.Numeric(14, 3), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    total_linea     = db.Column(db.Numeric(12, 2), nullable=False)

    producto = db.relationship('Productos')

    @property
    def id(self):
        return self.id_detalle