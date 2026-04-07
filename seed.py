from app import app, db, user_datastore
from flask_security import hash_password
import uuid

with app.app_context():
    # Crear roles si no existen
    admin_rol = user_datastore.find_or_create_role(name='ADMINISTRADOR', description='Control total')
    user_datastore.find_or_create_role(name='VENTAS', description='Gestión de ventas')
    
    # Crear usuario Admin por defecto
    if not user_datastore.find_user(email='admin@concretum.com'):
        admin_user = user_datastore.create_user(
            username='admin',
            email='admin@concretum.com',
            password=hash_password('12345678'), 
            fs_uniquifier=str(uuid.uuid4()),
            active=True
        )
        user_datastore.add_role_to_user(admin_user, admin_rol)
        db.session.commit()
        print("Usuario Admin creado exitosamente: admin@concretum.com / 12345678")
    else:
        print("El usuario Admin ya existe.")