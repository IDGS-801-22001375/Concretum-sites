from flask_security import UserMixin, RoleMixin
from datetime import datetime
from .extensions import db

usuario_roles = db.Table('usuario_roles',
    db.Column('usuario_id', db.BigInteger, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True),
    db.Column('rol_id',     db.BigInteger, db.ForeignKey('roles.id_rol',     ondelete='RESTRICT'), primary_key=True),
    db.Column('asignado_en', db.DateTime, default=datetime.utcnow)
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id_rol      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name        = db.Column('nombre',     db.String(80),  unique=True, nullable=False)  # Flask-Security requiere 'name'
    description = db.Column('descripcion', db.String(255))
    es_activo   = db.Column(db.Boolean, default=True)

    @property
    def id(self):
        return self.id_rol

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id_usuario        = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username          = db.Column(db.String(80),  unique=True, nullable=False)
    email             = db.Column(db.String(254), unique=True, nullable=False)
    password          = db.Column('password_hash', db.String(255), nullable=False)
    active            = db.Column('es_activo', db.Boolean, default=True)
    fs_uniquifier     = db.Column(db.String(255), unique=True, nullable=False)
    intentos_fallidos = db.Column(db.Integer, default=0)
    ultima_sesion     = db.Column(db.DateTime)
    tf_primary_method = db.Column(db.String(140), nullable=True)
    tf_totp_secret    = db.Column(db.String(255), nullable=True)

    roles = db.relationship('Role', secondary=usuario_roles, backref=db.backref('usuarios', lazy='dynamic'))

    @property
    def id(self):
        return self.id_usuario