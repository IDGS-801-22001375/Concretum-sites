from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify, session, send_file, flash
from config import Config
from models import db, User, Role
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user
from flask_security.signals import user_authenticated
from flask_login.signals import user_logged_out
from flask_login import login_user, logout_user, LoginManager
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
import jwt
import datetime
import logging
import qrcode
from io import BytesIO
import base64
import pyotp

logging.basicConfig(level=logging.DEBUG)

from usuarios import usuarios_bp
from materia_prima import materia_prima_bp
from proveedores import proveedores_bp
from forms import LoginFormSimple

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
db.init_app(app)

mongo_client = MongoClient(app.config['MONGO_URI'])
mongo_db = mongo_client.get_database()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, login_form=LoginFormSimple)

# Configuramos Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'security.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

app.register_blueprint(usuarios_bp)
app.register_blueprint(materia_prima_bp)
app.register_blueprint(proveedores_bp) 

# CORRECCIÓN: el user_loader debe buscar por fs_uniquifier, no por id numérico
@login_manager.user_loader
def load_user(user_id):
    # user_id es el fs_uniquifier (string)
    return User.query.filter_by(fs_uniquifier=user_id).first()

@app.context_processor
def inject_session():
    return dict(session=session)

@app.route('/favicon.ico')
def favicon():
    return make_response('', 204)

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
    if user:
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

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html')

# ============================================================================
# VISTA DE LOGIN PERSONALIZADA (reemplaza la de Flask-Security)
# ============================================================================
def custom_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginFormSimple()
    if form.validate_on_submit():
        user = form.user
        if user.tf_primary_method:
            session['pending_2fa_user_id'] = user.id
            return redirect(url_for('verificar_2fa'))
        else:
            login_user(user)
            next_page = request.args.get('next') or url_for('dashboard')
            return redirect(next_page)
    return render_template('auth/login.html', login_user_form=form)

# Reemplazar la vista de login de Flask-Security por la nuestra
app.view_functions['security.login'] = custom_login

# ============================================================================
# Ruta PERSONALIZADA para verificar el código 2FA (página simple)
# ============================================================================
@app.route('/verificar-2fa', methods=['GET', 'POST'])
def verificar_2fa():
    user_id = session.get('pending_2fa_user_id')
    if not user_id:
        flash('No hay una sesión de verificación activa.', 'error')
        return redirect(url_for('security.login'))

    user = User.query.get(user_id)   # user_id es numérico porque lo guardamos como user.id
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
                flash('El usuario no tiene 2FA configurado. Contacta al administrador.', 'error')
                return redirect(url_for('security.login'))
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                login_user(user)
                session.pop('pending_2fa_user_id', None)
                next_page = request.args.get('next') or url_for('dashboard')
                return redirect(next_page)
            else:
                flash('Código incorrecto. Inténtalo de nuevo.', 'error')
        return render_template('auth/verificar_2fa.html')

    return render_template('auth/verificar_2fa.html')

# ============================================================================
# Ruta PERSONALIZADA para configurar 2FA (con sidebar, dentro del dashboard)
# ============================================================================
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
        return render_template('security/custom_2fa.html', 
                               activado=True,
                               metodo=current_user.tf_primary_method)

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
                flash('2FA activado correctamente. A partir de ahora deberás ingresar el código al iniciar sesión.', 'success')
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
        return render_template('security/custom_2fa.html', 
                               activado=False,
                               qr_base64=qr_base64,
                               secret=secret)
    else:
        return render_template('security/custom_2fa.html', activado=False)

if __name__ == '__main__':
    app.run(debug=True, port=5000)