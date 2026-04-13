from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from flask_wtf.recaptcha import RecaptchaField
from flask_security.forms import RegisterForm
from models import db, User, Role
import datetime
import re

class LoginFormSimple(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Ingresar')

    def validate(self, **kwargs):
        if not super().validate():
            return False
        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            from app import mongo_db
            mongo_db.auditoria_eventos.insert_one({
                "usuario_id": None,
                "evento": "Login Fallido",
                "detalles": f"Intento con email no registrado: {self.email.data}",
                "modulo": "LOGIN",
                "user_agent": request.headers.get('User-Agent'),
                "ip": request.remote_addr,
                "fecha_creacion": datetime.datetime.utcnow()
            })
            self.email.errors.append('Credenciales incorrectas')
            return False
        if not self.user.verify_and_update_password(self.password.data):
            from app import mongo_db
            self.user.intentos_fallidos += 1
            mongo_db.auditoria_eventos.insert_one({
                "usuario_id": self.user.id,
                "evento": "Login Fallido",
                "detalles": f"Intento incorrecto #{self.user.intentos_fallidos}",
                "modulo": "LOGIN",
                "user_agent": request.headers.get('User-Agent'),
                "ip": request.remote_addr,
                "fecha_creacion": datetime.datetime.utcnow()
            })
            if self.user.intentos_fallidos >= 3:
                self.user.active = False
                self.email.errors.append('Cuenta bloqueada por seguridad tras 3 intentos.')
            db.session.commit()
            self.email.errors.append('Credenciales incorrectas')
            return False
        self.user.intentos_fallidos = 0
        db.session.commit()
        return True


class UsuarioForm(FlaskForm):
    id_usuario = HiddenField()
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    cambiar_password = BooleanField('Cambiar Contraseña', default=False)
    password = PasswordField('Contraseña', validators=[
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    roles = SelectMultipleField('Roles', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Usuario')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles.choices = [(r.id_rol, r.name) for r in Role.query.filter_by(es_activo=True).all()]

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (not self.id_usuario.data or user.id_usuario != int(self.id_usuario.data)):
            raise ValidationError('Este correo electrónico ya está registrado.')

    def validate(self, extra_validators=None):
        # Si es edición y no se marca cambiar_password, la contraseña es opcional
        if self.id_usuario.data and not self.cambiar_password.data:
            # Eliminar validadores de longitud y required temporalmente
            self.password.validators = [Optional()]
            self.confirm_password.validators = [Optional()]
        return super().validate(extra_validators)
    

class ExtendedRegisterForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(message='Ingresa un email válido')])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_password(self, field):
        password = field.data
        if not re.search(r'[A-Z]', password):
            raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
        if not re.search(r'\d', password):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[@$!%*?&._-]', password):
            raise ValidationError('La contraseña debe contener al menos un carácter especial (@, $, !, %, *, ?, &, ., _, -).')