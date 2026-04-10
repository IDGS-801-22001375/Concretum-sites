from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify, session, send_file, flash
from config import Config, DevelopmentConfig
from models import db, User, Role, MateriaPrima, ExistenciaMateriaPrima, Produccion, Merma, Productos, CategoriasProducto, Venta, VentaDetalle, CorteCaja, CorteDesglose, Cliente
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user
from flask_login.signals import user_logged_out
from flask_security.signals import user_authenticated, user_registered
from flask_login import login_user, logout_user, LoginManager
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
from forms import LoginFormSimple, ExtendedRegisterForm
from flask_security.registerable import register_user
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
import jwt
import datetime
import logging
import qrcode
from io import BytesIO
import base64
import pyotp

logging.basicConfig(level=logging.DEBUG)

# Importación de blueprints
from routes.usuarios import usuarios_bp
from routes.materia_prima import materia_prima_bp
from routes.proveedores import proveedores_bp
from routes.compras import compras_bp
from routes.mermas import mermas_bp
from routes.configuracion import configuracion_bp
from routes.productos import productos_bp
#from routes.inventario import inventario_bp
from routes.auditoria import auditoria_bp
from routes.recetas import recetas_bp
from routes.comercial import comercial_bp
from routes.clientes import clientes_bp
from routes.inventario_produccion import stock_bp
from routes.produccion_recetas import produccion_recetas_bp
from routes.carrito import carrito_bp  

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
csrf = CSRFProtect(app)
db.init_app(app)

mongo_client = MongoClient(app.config['MONGO_URI'])
mongo_db = mongo_client.get_database()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, login_form=LoginFormSimple, register_form=ExtendedRegisterForm)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'security.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Registro de blueprints
app.register_blueprint(productos_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(comercial_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(materia_prima_bp)
app.register_blueprint(compras_bp)
#app.register_blueprint(inventario_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(mermas_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(produccion_recetas_bp)
app.register_blueprint(carrito_bp) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(fs_uniquifier=user_id).first()

@app.context_processor
def inject_session():
    return dict(session=session)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/logoConcretum.ico'))

@user_authenticated.connect_via(app)
def on_user_authenticated(app, user, **extra):
    try:
        access_token = jwt.encode({
            'user_id': user.id,
            'type': 'access',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        refresh_token = jwt.encode({
            'user_id': user.id,
            'type': 'refresh',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        request.environ['set_jwt_access'] = access_token
        request.environ['set_jwt_refresh'] = refresh_token
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": user.id,
            "evento": "Inicio de Sesión",
            "detalles": "Autenticación exitosa - JWT emitido",
            "modulo": "LOGIN",
            "user_agent": request.headers.get('User-Agent'),
            "ip": request.remote_addr,
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        app.logger.error(f"Error en on_user_authenticated: {e}")

@user_logged_out.connect_via(app)
def on_user_logout(app, user, **extra):
    if user and hasattr(user, 'id') and user.id is not None:
        try:
            mongo_db.auditoria_eventos.insert_one({
                "usuario_id": user.id,
                "evento": "Cierre de Sesión",
                "detalles": "Sesión finalizada por el usuario",
                "modulo": "LOGIN",
                "user_agent": request.headers.get('User-Agent'),
                "fecha_creacion": datetime.datetime.utcnow()
            })
        except Exception as e:
            app.logger.error(f"Error registrando logout en Mongo: {e}")

@app.after_request
def attach_jwt_cookies(response):
    access = request.environ.get('set_jwt_access')
    refresh = request.environ.get('set_jwt_refresh')
    is_secure = app.config.get('ENV') == 'production'
    if access:
        response.set_cookie('access_token', access, httponly=True, samesite='Lax', secure=is_secure)
        response.set_cookie('refresh_token', refresh, httponly=True, samesite='Lax', secure=is_secure)
    return response

@app.route('/refresh', methods=['POST'])
@csrf.exempt
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "No refresh token"}), 401
    try:
        payload = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return jsonify({"error": "Tipo de token inválido"}), 401
        nuevo_access = jwt.encode({
            'user_id': payload['user_id'],
            'type': 'access',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        resp = make_response(jsonify({"message": "Token renovado con éxito"}))
        resp.set_cookie('access_token', nuevo_access, httponly=True, samesite='Lax',
                        secure=(app.config.get('ENV') == 'production'))
        return resp
    except Exception:
        return jsonify({"error": "Token inválido o expirado"}), 401

@app.route("/")
def index():
    productos_lista = db.session.query(Productos)\
        .join(CategoriasProducto, Productos.categoria_id == CategoriasProducto.id_categoria)\
        .filter(Productos.es_active == 1)\
        .order_by(Productos.fecha_creacion.desc())\
        .limit(6)\
        .all()
    return render_template("/home/index.html", productos_lista=productos_lista)

@app.route("/admin")
def admin():
    return render_template("/base.html")

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

@app.errorhandler(Exception)
def handle_global_exception(e):
    """Atrapa cualquier error 500 o excepción no manejada en toda la app."""
    
    if isinstance(e, HTTPException):
        return e

    app.logger.error(f"Error crítico del sistema: {str(e)}", exc_info=True)

    is_api = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.path.startswith('/api') or 
        '/api/' in request.path
    )

    if is_api:
        return jsonify({
            'success': False,
            'message': 'Ocurrió un error interno en el servidor. El equipo técnico ha sido notificado.'
        }), 500

    flash('Ocurrió un error inesperado en la plataforma. Intenta nuevamente.', 'error')
    
    return redirect(request.referrer or url_for('comercial_bp.dashboard'))

def custom_login():
    if current_user.is_authenticated:
        return redirect(url_for('comercial_bp.dashboard'))
    form = LoginFormSimple()
    if form.validate_on_submit():
        user = form.user
        if user.tf_primary_method:
            token = serializer.dumps(user.id)
            return redirect(url_for('verificar_2fa', token=token))
        else:
            login_user(user)
            user.ultima_sesion = datetime.datetime.now()
            db.session.commit()

            if user.has_role('CLIENTE'):
                return redirect(url_for('carrito_bp.catalogo'))

            next_page = request.args.get('next') or url_for('comercial_bp.dashboard')
            return redirect(next_page)
    return render_template('auth/login.html', login_user_form=form)

app.view_functions['security.login'] = custom_login

# Registro personalizado para evitar el auto-login
def custom_register():
    if current_user.is_authenticated:
        return redirect(url_for('comercial_bp.dashboard'))

    form = ExtendedRegisterForm()

    if request.method == 'POST':
        app.logger.debug(f"Datos del formulario: {request.form}")
        app.logger.debug(f"Errores de validación (antes de validate): {form.errors}")

    if form.validate_on_submit():
        app.logger.debug("Formulario validado correctamente")
        try:
            # Verificar duplicados manualmente
            if User.query.filter_by(email=form.email.data).first():
                flash('El correo electrónico ya está registrado.', 'danger')
                return render_template('auth/register.html', register_user_form=form)

            if User.query.filter_by(username=form.username.data).first():
                flash('El nombre de usuario ya está en uso.', 'danger')
                return render_template('auth/register.html', register_user_form=form)

            from flask_security import hash_password
            import uuid

            # Crear usuario con rol CLIENTE
            nuevo_usuario = User(
                username=form.username.data,
                email=form.email.data,
                password=hash_password(form.password.data),
                fs_uniquifier=str(uuid.uuid4()),
                active=True,
                intentos_fallidos=0
            )
            db.session.add(nuevo_usuario)
            db.session.flush()  # para obtener ID

            # Asegurar rol CLIENTE
            cliente_role = Role.query.filter_by(name='CLIENTE').first()
            if not cliente_role:
                cliente_role = Role(name='CLIENTE', description='Usuario cliente', es_activo=True)
                db.session.add(cliente_role)
                db.session.flush()

            nuevo_usuario.roles.append(cliente_role)

            # Crear registro en clientes vinculado al usuario
            nuevo_cliente = Cliente(
                usuario_id=nuevo_usuario.id,
                razon_social=form.username.data,   # o podrías poner el nombre completo después
                email=form.email.data,
                es_activo=1
            )
            db.session.add(nuevo_cliente)

            db.session.commit()
            app.logger.info(f"Usuario {nuevo_usuario.email} registrado con rol CLIENTE y cliente asociado")

            flash('¡Cuenta creada exitosamente! Por favor, inicia sesión.', 'success')
            return redirect(url_for('security.login'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"ERROR en registro: {str(e)}", exc_info=True)
            flash(f'Error inesperado: {str(e)}', 'danger')
            return render_template('auth/register.html', register_user_form=form)
    else:
        for field, field_errors in form.errors.items():
            for error in field_errors:
                flash(f'Error en {getattr(form, field).label.text}: {error}', 'danger')
        if not form.errors:
            flash('Por favor completa todos los campos correctamente.', 'danger')

    return render_template('auth/register.html', register_user_form=form)

# Sobrescribimos la ruta original de Flask-Security
app.view_functions['security.register'] = custom_register

@app.route('/verificar-2fa', methods=['GET', 'POST'])
def verificar_2fa():
    token = request.args.get('token')
    if not token:
        flash('Enlace de verificación inválido', 'error')
        return redirect(url_for('security.login'))

    try:
        user_id = serializer.loads(token, max_age=300)  
    except Exception:
        flash('El enlace ha expirado o es inválido', 'error')
        return redirect(url_for('security.login'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('security.login'))

    if request.method == 'POST':
        code = request.form.get('codigo')
        if not code:
            flash('Debes ingresar el código de 6 dígitos.', 'error')
        else:
            secret = user.tf_totp_secret
            if not secret:
                flash('El usuario no tiene 2FA configurado.', 'error')
                return redirect(url_for('security.login'))
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                login_user(user)
                user.ultima_sesion = datetime.datetime.now()
                db.session.commit()
                next_page = request.args.get('next') or url_for('comercial_bp.dashboard')
                return redirect(next_page)
            else:
                flash('Código incorrecto. Inténtalo de nuevo.', 'error')
        return render_template('auth/verificar_2fa.html', token=token)

    return render_template('auth/verificar_2fa.html', token=token)

@app.route('/configurar-2fa', methods=['GET', 'POST'])
@login_required
def configurar_2fa():
    es_cliente = current_user.has_role('CLIENTE')
    template_name = 'tienda/2fa_config.html' if es_cliente else 'security/custom_2fa.html'
    
    if current_user.tf_primary_method:
        if request.method == 'POST' and request.form.get('action') == 'disable':
            current_user.tf_primary_method = None
            current_user.tf_totp_secret = None
            db.session.commit()
            flash('2FA desactivado correctamente.', 'success')
            return redirect(url_for('configurar_2fa'))
        return render_template(template_name, activado=True, metodo=current_user.tf_primary_method)
    
    if request.method == 'POST':
        if 'codigo' in request.form:
            secret = current_user.tf_totp_secret
            if not secret:
                flash('Primero debes generar el código QR.', 'error')
                return redirect(url_for('configurar_2fa'))
            totp = pyotp.TOTP(secret)
            if totp.verify(request.form['codigo']):
                current_user.tf_primary_method = 'authenticator'
                db.session.commit()
                flash('2FA activado correctamente.', 'success')
                return redirect(url_for('configurar_2fa'))
            else:
                flash('Código incorrecto. Inténtalo de nuevo.', 'error')
                return redirect(url_for('configurar_2fa'))
        else:
            if not current_user.tf_totp_secret:
                current_user.tf_totp_secret = pyotp.random_base32()
                db.session.commit()
            return redirect(url_for('configurar_2fa'))
    
    secret = current_user.tf_totp_secret
    if secret:
        uri = f"otpauth://totp/CRM_Concretum:{current_user.email}?secret={secret}&issuer=CRM_Concretum"
        qr = qrcode.make(uri)
        img_io = BytesIO()
        qr.save(img_io, 'PNG')
        img_io.seek(0)
        qr_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return render_template(template_name, activado=False, qr_base64=qr_base64, secret=secret)
    else:
        return render_template(template_name, activado=False)

@app.context_processor
def inject_sidebar_counts():
    from models import ConfiguracionEmpresa, Existencias, Productos, MateriaPrima, ExistenciaMateriaPrima, Merma, Produccion, PedidoCliente, SolicitudProduccion
    config = ConfiguracionEmpresa.query.first()
    
    criticos_mp = 0
    criticos_prod = 0
    mermas_recientes = 0

    if config and config.alerta_stock_minimo:
        criticos_mp = db.session.query(MateriaPrima).join(
            ExistenciaMateriaPrima,
            MateriaPrima.id_materia_prima == ExistenciaMateriaPrima.materia_prima_id
        ).filter(
            MateriaPrima.es_activo == True,
            MateriaPrima.stock_minimo > 0,
            ExistenciaMateriaPrima.stock_actual < MateriaPrima.stock_minimo
        ).count()

        criticos_prod = db.session.query(Existencias).join(
            Productos,
            Existencias.producto_id == Productos.id_producto
        ).filter(
            Productos.es_active == 1,
            Existencias.estado_stock == 'BAJO'
        ).count()

    if config and config.alerta_merma_diaria:
        hace_7dias = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        mermas_recientes = Merma.query.filter(
            Merma.fecha_registro >= hace_7dias
        ).count()

    producciones_activas = Produccion.query.filter_by(estado='EN_PROCESO').count()
    
    pedidos_por_autorizar = PedidoCliente.query.filter_by(estado='COTIZACION').count()
    solicitudes_prod = SolicitudProduccion.query.filter_by(estado='PENDIENTE').count()

    return {
        'sidebar_criticos_mp': criticos_mp,
        'sidebar_criticos_prod': criticos_prod,
        'sidebar_pedidos': producciones_activas,
        'sidebar_mermas': mermas_recientes,
        'sidebar_pedidos_autorizar': pedidos_por_autorizar,
        'sidebar_solicitudes_prod': solicitudes_prod
    }

@app.context_processor
def inject_config():
    from models import ConfiguracionEmpresa
    config = ConfiguracionEmpresa.query.first()
    if not config:
        config = ConfiguracionEmpresa()
        db.session.add(config)
        db.session.commit()
    return dict(config_empresa=config)

if __name__ == '__main__':
    app.run(debug=True, port=5000)