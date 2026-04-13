from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_security import login_required, roles_accepted, hash_password, current_user
from . import usuarios_bp
from models import db, User, Role
from forms import UsuarioForm
import uuid
import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, asc, desc
import threading
from copy import copy

def _guardar_en_mongo(datos_auditoria):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one(datos_auditoria)
    except Exception as e:
        print(f"Error Mongo (Async): {e}")

def registrar_auditoria(usuario_accion, accion, detalles):
    user_agent = request.headers.get('User-Agent') if request else 'Desconocido'
    ip_addr = request.remote_addr if request else '0.0.0.0'
    
    datos_auditoria = {
        "usuario_id": usuario_accion,
        "evento": accion,
        "detalles": detalles,
        "modulo": "Nombre del Modulo",
        "user_agent": user_agent,
        "ip": ip_addr,
        "fecha_creacion": datetime.datetime.utcnow()
    }
    
    threading.Thread(target=_guardar_en_mongo, args=(datos_auditoria,)).start()

@usuarios_bp.route('/usuarios', methods=['GET', 'POST'])
@login_required
@roles_accepted('ADMINISTRADOR')
def index():
    roles_list = Role.query.filter_by(es_activo=True).all()
    role_options = [{'value': r.id_rol, 'label': r.name} for r in roles_list]
    return render_template('usuarios/index.html', roles_list=roles_list, role_options=role_options)

@usuarios_bp.route('/usuarios/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR')
def api_usuarios():
    """API para obtener usuarios paginados, filtrados y ordenados"""
    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    # Parámetros de ordenamiento
    sort_by = request.args.get('sort_by', 'username')
    sort_order = request.args.get('sort_order', 'asc')
    # Parámetros de filtro
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    active_filter = request.args.get('active', '')

    query = User.query

    # Filtros
    if search:
        query = query.filter(or_(
            User.username.ilike(f'%{search}%'),
            User.email.ilike(f'%{search}%')
        ))
    if role_filter:
        query = query.filter(User.roles.any(Role.id_rol == int(role_filter)))
    if active_filter:
        if active_filter == 'true':
            query = query.filter(User.active == True)
        elif active_filter == 'false':
            query = query.filter(User.active == False)

    # Ordenamiento
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(User, sort_by, User.username)))
    else:
        query = query.order_by(desc(getattr(User, sort_by, User.username)))

    # Paginación
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Construir respuesta
    items = []
    for user in paginated.items:
        items.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'es_activo': user.active,                # ← campo unificado
            'roles': [{'id': r.id_rol, 'name': r.name} for r in user.roles],
            'ultima_sesion': user.ultima_sesion.strftime('%Y-%m-%d %H:%M') if user.ultima_sesion else None
        })

    return jsonify({
        'items': items,                              # ← clave unificada
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@usuarios_bp.route('/usuarios/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR')
def guardar_usuario():
    form = UsuarioForm()
    if form.validate_on_submit():
        if form.id_usuario.data:
            # Edición
            user = User.query.get_or_404(int(form.id_usuario.data))
            # No permitir que un usuario se suba de rol si no es ADMIN
            if user.id == current_user.id and 'ADMINISTRADOR' not in [r.name for r in current_user.roles]:
                return jsonify({'success': False, 'errors': {'general': 'No puedes modificar tu propio rol.'}}), 400
            # Actualizar datos
            user.username = form.username.data
            user.email = form.email.data
            if form.cambiar_password.data and form.password.data:
                user.password = hash_password(form.password.data)
            # Actualizar roles
            user.roles = []
            for role_id in form.roles.data:
                role = Role.query.get(role_id)
                if role:
                    user.roles.append(role)
            db.session.commit()
            registrar_auditoria(current_user.id, "Editar Usuario", f"Usuario editado: {user.email}")
            return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente.'})
        else:
            # Creación
            if not form.password.data:
                return jsonify({'success': False, 'errors': {'password': 'La contraseña es obligatoria para un nuevo usuario.'}}), 400
            try:
                nuevo_usuario = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hash_password(form.password.data),
                    fs_uniquifier=str(uuid.uuid4()),
                    active=True,
                    intentos_fallidos=0
                )
                for role_id in form.roles.data:
                    role = Role.query.get(role_id)
                    if role:
                        nuevo_usuario.roles.append(role)
                db.session.add(nuevo_usuario)
                db.session.commit()
                registrar_auditoria(current_user.id, "Crear Usuario", f"Usuario creado: {nuevo_usuario.email}")
                return jsonify({'success': True, 'message': 'Usuario creado exitosamente.'})
            except IntegrityError:
                db.session.rollback()
                return jsonify({'success': False, 'errors': {'email': 'El correo electrónico ya está registrado.'}}), 400
    else:
        # Errores de validación
        errors = {}
        for field, field_errors in form.errors.items():
            if field == 'csrf_token':
                continue
            errors[field] = field_errors[0] if field_errors else 'Campo inválido'
        return jsonify({'success': False, 'errors': errors}), 400

@usuarios_bp.route('/usuarios/obtener/<int:id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR')
def obtener_usuario(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'active': user.active,
        'roles': [r.id_rol for r in user.roles]   # array de IDs
    })

@usuarios_bp.route('/usuarios/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR')
def alternar_estado(id):
    if id == current_user.id:
        return jsonify({'success': False, 'message': 'No puedes desactivar tu propia cuenta.'}), 400
    usuario = User.query.get_or_404(id)
    usuario.active = not usuario.active 
    if usuario.active:
        usuario.intentos_fallidos = 0
    estado_txt = "Activado" if usuario.active else "Baja/Bloqueado"
    registrar_auditoria(current_user.id, "Estatus Usuario", f"Usuario {usuario.email} cambiado a {estado_txt}")
    db.session.commit()
    return jsonify({'success': True, 'message': f'Usuario {usuario.email} ahora está {estado_txt.lower()}.'})