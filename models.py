from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime, timedelta
import enum

db = SQLAlchemy()

# Tabla Intermedia MySQL: usuario_roles
usuario_roles = db.Table('usuario_roles',
    db.Column('usuario_id', db.BigInteger, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    db.Column('rol_id', db.BigInteger, db.ForeignKey('roles.id_rol', ondelete='RESTRICT'), primary_key=True),
    db.Column('asignado_en', db.DateTime, default=datetime.utcnow)
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id_rol = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column('nombre', db.String(80), unique=True, nullable=False) # Flask-Security requiere el atributo 'name'
    description = db.Column('descripcion', db.String(255))
    es_activo = db.Column(db.Boolean, default=True)
    
    # Para compatibilidad con Flask-Security
    @property
    def id(self):
        return self.id_rol

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column('password_hash', db.String(255), nullable=False)
    active = db.Column('es_activo', db.Boolean, default=True) 
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False) 
    intentos_fallidos = db.Column(db.Integer, default=0)
    ultima_sesion = db.Column(db.DateTime)
    tf_primary_method = db.Column(db.String(140), nullable=True)
    tf_totp_secret = db.Column(db.String(255), nullable=True)
    
    roles = db.relationship('Role', secondary=usuario_roles, backref=db.backref('usuarios', lazy='dynamic'))

    @property
    def id(self):
        return self.id_usuario
    

# ====================== MATERIA PRIMA ======================
class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'
    id_materia_prima = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    unidad_medida = db.Column(db.Enum('KG','TON','M3','LTS'), nullable=False)
    proveedor_id = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor', ondelete='RESTRICT'), nullable=False)
    stock_minimo = db.Column(db.Numeric(14,3), default=0)
    costo_unitario = db.Column(db.Numeric(12,2), default=0)
    es_activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    proveedor = db.relationship('Proveedor', backref='materias_primas')
    existencia = db.relationship('ExistenciaMateriaPrima', uselist=False, back_populates='materia_prima', cascade='all, delete-orphan')

    @property
    def id(self):
        return self.id_materia_prima

class ExistenciaMateriaPrima(db.Model):
    __tablename__ = 'existencias_materia_prima'
    id_existencia_mp = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    materia_prima_id = db.Column(db.BigInteger, db.ForeignKey('materias_primas.id_materia_prima', ondelete='RESTRICT'), unique=True, nullable=False)
    stock_actual = db.Column(db.Numeric(14,3), default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    materia_prima = db.relationship('MateriaPrima', back_populates='existencia')

class CategoriaProveedor(enum.Enum):
    MATERIA_PRIMA = "MATERIA_PRIMA"
    SERVICIOS = "SERVICIOS"
    INSUMOS = "INSUMOS"


# ====================== ENUM PARA CATEGORÍA DE PROVEEDOR ======================
class CategoriaProveedor(enum.Enum):
    MATERIA_PRIMA = "MATERIA_PRIMA"
    SERVICIOS = "SERVICIOS"
    INSUMOS = "INSUMOS"

# ====================== MODELO PROVEEDOR (ampliado) ======================
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id_proveedor = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    razon_social = db.Column(db.String(200), nullable=False)
    rfc = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(254), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    contacto = db.Column(db.String(100))                     # persona de contacto
    telefono_contacto = db.Column(db.String(15))
    domicilio = db.Column(db.Text)
    categoria = db.Column(db.Enum(CategoriaProveedor), default=CategoriaProveedor.MATERIA_PRIMA)
    dias_credito = db.Column(db.Integer, default=0)
    limite_credito = db.Column(db.Numeric(12,2), default=0)
    es_activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con compras
    compras = db.relationship('Compra', backref='proveedor', lazy='dynamic')

    @property
    def total_compras(self):
        """Suma total de todas las compras de este proveedor"""
        from sqlalchemy import func
        total = db.session.query(func.sum(Compra.total)).filter(Compra.proveedor_id == self.id_proveedor).scalar()
        return float(total or 0)

    @property
    def compras_ultimo_mes(self):
        """Suma de compras del último mes"""
        from sqlalchemy import func
        ultimo_mes = datetime.utcnow() - timedelta(days=30)
        total = db.session.query(func.sum(Compra.total)).filter(
            Compra.proveedor_id == self.id_proveedor,
            Compra.fecha_compra >= ultimo_mes
        ).scalar()
        return float(total or 0)

    @property
    def cuentas_vencidas(self):
        """Lista de pagos vencidos (fecha_vencimiento < hoy y no pagados)"""
        hoy = datetime.utcnow().date()
        vencidos = PagoProveedor.query.filter(
            PagoProveedor.compra.has(proveedor_id=self.id_proveedor),
            PagoProveedor.fecha_vencimiento < hoy,
            PagoProveedor.fecha_pago == None
        ).all()
        return vencidos

    @property
    def monto_vencido(self):
        return sum(p.monto for p in self.cuentas_vencidas)

    @property
    def id(self):
        return self.id_proveedor

# ====================== MODELO COMPRA (básico) ======================
class Compra(db.Model):
    __tablename__ = 'compras'
    id_compra = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    proveedor_id = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor', ondelete='RESTRICT'), nullable=False)
    folio = db.Column(db.String(40), unique=True, nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(12,2), nullable=False, default=0)
    estado = db.Column(db.Enum('CREADA', 'RECIBIDA', 'CANCELADA'), default='CREADA')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con pagos
    pagos = db.relationship('PagoProveedor', backref='compra', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def id(self):
        return self.id_compra

# ====================== MODELO PAGO PROVEEDOR ======================
class PagoProveedor(db.Model):
    __tablename__ = 'pagos_proveedor'
    id_pago = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    compra_id = db.Column(db.BigInteger, db.ForeignKey('compras.id_compra', ondelete='RESTRICT'), nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    fecha_pago = db.Column(db.Date, nullable=True)
    monto = db.Column(db.Numeric(12,2), nullable=False)
    forma_pago = db.Column(db.Enum('EFECTIVO', 'TRANSFERENCIA', 'CHEQUE'), default='TRANSFERENCIA')
    estatus = db.Column(db.Enum('PENDIENTE', 'PAGADO', 'VENCIDO'), default='PENDIENTE')
    observaciones = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def id(self):
        return self.id_pago