from extensions import db
import datetime

class Proveedores(db.Model):
    __tablename__ = 'proveedores'
    id_proveedor = db.Column(db.Integer, primary_key = True)
    razon_social = db.Column(db.String(200))
    rfc = db.Column(db.String(20))
    email = db.Column(db.String(254))
    telefono = db.Column(db.String(10))
    es_activo = db.Column(db.Integer, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_actualizacion = db.Column(db.DateTime)