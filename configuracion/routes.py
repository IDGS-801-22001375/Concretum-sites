from flask import render_template, request, redirect, url_for, flash, current_app
from flask_security import login_required, roles_accepted, current_user
from models import db, ConfiguracionEmpresa
from . import configuracion_bp
from werkzeug.utils import secure_filename
import os
import datetime

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Configuración",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

@configuracion_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
@roles_accepted('ADMINISTRADOR')
def index():
    config = ConfiguracionEmpresa.query.first()
    if not config:
        config = ConfiguracionEmpresa()
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'POST':
        config.razon_social = request.form.get('razon_social')
        config.rfc = request.form.get('rfc')
        config.direccion = request.form.get('direccion')
        config.telefono = request.form.get('telefono')
        config.email_facturacion = request.form.get('email_facturacion')
        config.alerta_stock_minimo = 'alerta_stock_minimo' in request.form
        config.alerta_vencimiento_credito = 'alerta_vencimiento_credito' in request.form
        config.alerta_merma_diaria = 'alerta_merma_diaria' in request.form
        config.moneda = request.form.get('moneda')
        config.zona_horaria = request.form.get('zona_horaria')
        config.actualizado_por = current_user.id
        
        # Manejo de logo
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            # Generar nombre único para evitar colisiones
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{datetime.datetime.utcnow().timestamp()}{ext}"
            filepath = os.path.join(upload_folder, unique_filename)
            logo_file.save(filepath)
            # Guardar ruta relativa para la URL (desde static)
            config.logo = f'uploads/{unique_filename}'
        
        db.session.commit()
        registrar_auditoria(current_user.id, "Actualizar Configuración", 
                            f"Configuración actualizada por {current_user.email}")
        flash('Configuración guardada correctamente', 'success')
        return redirect(url_for('configuracion.index'))
    
    return render_template('configuracion/index.html', config=config)