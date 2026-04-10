from .extensions import db
from datetime import datetime


# ============================================================
# VENTAS
# ============================================================

class Venta(db.Model):
    __tablename__ = 'ventas'

    id_venta        = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    folio           = db.Column(db.String(40), nullable=False, unique=True)
    cliente_id      = db.Column(db.BigInteger, db.ForeignKey('clientes.id_cliente'), nullable=False)
    usuario_id      = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    metodo_pago = db.Column(db.Enum('EFECTIVO', 'TRANSFERENCIA', 'CHEQUE', 'CREDITO', 'TARJETA', 'OXXO'), nullable=False)
    estado          = db.Column(db.Enum('PENDIENTE', 'COBRADO', 'CREDITO', 'CANCELADO'), nullable=False, default='PENDIENTE')
    subtotal        = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    iva             = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    total           = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    fecha_venta     = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_creacion  = db.Column(db.DateTime, nullable=False, default=datetime.now)

    cliente         = db.relationship('Cliente', backref='ventas')
    detalle         = db.relationship('VentaDetalle', backref='venta', cascade='all, delete-orphan')


class VentaDetalle(db.Model):
    __tablename__ = 'venta_detalle'

    id_detalle      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    venta_id        = db.Column(db.BigInteger, db.ForeignKey('ventas.id_venta'), nullable=False)
    producto_id     = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario  = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    total_linea     = db.Column(db.Numeric(12, 2), nullable=False)

    producto        = db.relationship('Productos', backref='ventas_detalle')


# ============================================================
# CORTE DE CAJA
# ============================================================

class CorteCaja(db.Model):
    __tablename__ = 'cortes_caja'

    id_corte            = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    usuario_id          = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    periodo_inicio      = db.Column(db.DateTime, nullable=False)
    periodo_fin         = db.Column(db.DateTime, nullable=True)
    fondo_inicial       = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    total_ventas        = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    total_cobrado       = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    ventas_credito      = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    devoluciones        = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    salida_proveedores  = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    utilidad            = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    estado              = db.Column(db.Enum('ABIERTO', 'CERRADO'), nullable=False, default='ABIERTO')
    fecha_creacion      = db.Column(db.DateTime, nullable=False, default=datetime.now)

    desglose            = db.relationship('CorteDesglose', backref='corte', cascade='all, delete-orphan')


class CorteDesglose(db.Model):
    __tablename__ = 'corte_desglose'

    id_desglose     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    corte_id        = db.Column(db.BigInteger, db.ForeignKey('cortes_caja.id_corte'), nullable=False)
    forma_pago      = db.Column(db.String(50), nullable=False)
    operaciones     = db.Column(db.Integer, nullable=False, default=0)
    monto           = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    es_credito      = db.Column(db.Boolean, nullable=False, default=False)


# ============================================================
# CLIENTES
# ============================================================

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id_cliente          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    razon_social        = db.Column(db.String(200), nullable=False)
    rfc                 = db.Column(db.String(20), nullable=True)
    email               = db.Column(db.String(254), nullable=True)
    es_activo           = db.Column(db.SmallInteger, nullable=False, default=1)
    fecha_creacion      = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), unique=True, nullable=True)
    
    usuario = db.relationship('User', backref=db.backref('cliente_info', uselist=False))
    detalle_info        = db.relationship('ClienteDetalle', backref='cliente', uselist=False, cascade='all, delete-orphan')

class ClienteDetalle(db.Model):
    __tablename__ = 'cliente_detalle'

    id_detalle          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    cliente_id          = db.Column(db.BigInteger, db.ForeignKey('clientes.id_cliente', ondelete='CASCADE'), nullable=False)
    telefono            = db.Column(db.String(10), nullable=True)
    direccion           = db.Column(db.String(255), nullable=True)
    ciudad              = db.Column(db.String(50), nullable=True)
    estado              = db.Column(db.String(50), nullable=True)
    codigo_postal       = db.Column(db.String(5), nullable=True)
    notas               = db.Column(db.Text, nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)