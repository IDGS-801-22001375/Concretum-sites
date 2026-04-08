from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify, session, send_file, flash
from config import Config, DevelopmentConfig
from models import db, User, Role, MateriaPrima, ExistenciaMateriaPrima, Produccion, Merma, Productos, CategoriasProducto
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user
from flask_login.signals import user_logged_out
from flask_security.signals import user_authenticated, user_registered
from flask_login import login_user, logout_user, LoginManager
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
from forms import LoginFormSimple, ExtendedRegisterForm
from flask_security.registerable import register_user
import jwt
import datetime
import logging
import qrcode
from io import BytesIO
import base64
import pyotp

logging.basicConfig(level=logging.DEBUG)

from routes.usuarios import usuarios_bp
from routes.materia_prima import materia_prima_bp
from routes.proveedores import proveedores_bp
from routes.compras import compras_bp
from routes.mermas import mermas_bp
from routes.configuracion import configuracion_bp
from routes.productos import productos_bp
from routes.inventario import inventario_bp
from routes.recetas import recetas_bp
from routes.productos import productos_bp
from routes.comercial import comercial_bp
from routes.clientes import clientes_bp
from models import db, User, Role, MateriaPrima, ExistenciaMateriaPrima, Produccion, Merma, Venta, VentaDetalle, CorteCaja, CorteDesglose, Cliente

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
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
app.register_blueprint(inventario_bp)
app.register_blueprint(mermas_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(clientes_bp)

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
    if user and user.is_authenticated: 
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": user.id,
            "evento": "Cierre de Sesión",
            "detalles": "Sesión finalizada por el usuario",
            "modulo": "LOGIN",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })

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

# Login y dashboard de Cristian
def custom_login():
    if current_user.is_authenticated:
       return redirect(url_for('comercial_bp.dashboard')) 
    form = LoginFormSimple()
    if form.validate_on_submit():
        user = form.user
        if user.tf_primary_method:
            session['pending_2fa_user_id'] = user.id
            return redirect(url_for('verificar_2fa'))
        else:
            login_user(user)
            next_page = request.args.get('next') or url_for('comercial_bp.dashboard')
            return redirect(next_page)
    return render_template('auth/login.html', login_user_form=form)

app.view_functions['security.login'] = custom_login

# Registro personalizado para evitar el auto-login
def custom_register():
    if current_user.is_authenticated:
        return redirect(url_for('comercial_bp.dashboard'))
    
    form = ExtendedRegisterForm()
    if form.validate_on_submit():
        # Esto crea al usuario, encripta su contraseña y lo guarda
        user = register_user(form)
        db.session.commit()
        
        flash('¡Cuenta creada exitosamente! Por favor, inicia sesión con tus nuevas credenciales.', 'success')
        # Lo redirigimos AL LOGIN a la fuerza
        return redirect(url_for('security.login'))
        
    return render_template('auth/register.html', register_user_form=form)

# Sobrescribimos la ruta original de Flask-Security
app.view_functions['security.register'] = custom_register

@app.route('/verificar-2fa', methods=['GET', 'POST'])
def verificar_2fa():
    user_id = session.get('pending_2fa_user_id')
    if not user_id:
        flash('No hay una sesión de verificación activa.', 'error')
        return redirect(url_for('security.login'))
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado.', 'error')
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
                session.pop('pending_2fa_user_id', None)
                next_page = request.args.get('next') or url_for('comercial_bp.dashboard') 
                return redirect(next_page)
            else:
                flash('Código incorrecto. Inténtalo de nuevo.', 'error')
        return render_template('auth/verificar_2fa.html')
    return render_template('auth/verificar_2fa.html')

@app.route('/configurar-2fa', methods=['GET', 'POST'])
@login_required
def configurar_2fa():
    if current_user.tf_primary_method:
        if request.method == 'POST' and request.form.get('action') == 'disable':
            current_user.tf_primary_method = None
            current_user.tf_totp_secret = None
            db.session.commit()
            flash('2FA desactivado correctamente.', 'success')
            return redirect(url_for('configurar_2fa'))
        return render_template('security/custom_2fa.html', activado=True, metodo=current_user.tf_primary_method)
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
        return render_template('security/custom_2fa.html', activado=False, qr_base64=qr_base64, secret=secret)
    else:
        return render_template('security/custom_2fa.html', activado=False)

@app.context_processor
def inject_sidebar_counts():
    from models import ConfiguracionEmpresa
    config = ConfiguracionEmpresa.query.first()
    criticos = 0
    mermas_recientes = 0
    if config and config.alerta_stock_minimo:
        
        criticos = db.session.query(MateriaPrima).join(
            ExistenciaMateriaPrima,
            MateriaPrima.id_materia_prima == ExistenciaMateriaPrima.materia_prima_id
        ).filter(
            MateriaPrima.es_activo == True,
            MateriaPrima.stock_minimo > 0,
            ExistenciaMateriaPrima.stock_actual < MateriaPrima.stock_minimo
        ).count()
    if config and config.alerta_merma_diaria:
        hace_7dias = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        mermas_recientes = Merma.query.filter(Merma.fecha_registro >= hace_7dias).count()
    producciones_activas = Produccion.query.filter_by(estado='EN_PROCESO').count()
    return {
        'sidebar_criticos': criticos,
        'sidebar_pedidos': producciones_activas,
        'sidebar_mermas': mermas_recientes
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
    app.run(debug=True, port=5001)
