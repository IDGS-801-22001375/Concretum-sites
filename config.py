import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.environ.get('MONGO_URI')
    
    ENV = os.environ.get('FLASK_ENV', 'development')

    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    
    SECURITY_LOGIN_USER_TEMPLATE = 'auth/login.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'auth/register.html'
    SECURITY_POST_LOGIN_VIEW = '/dashboard'
    SECURITY_POST_LOGOUT_VIEW = '/login'
    
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    
    # Desactivamos el 2FA nativo porque usaremos nuestra propia implementación
    SECURITY_TWO_FACTOR = False
    
    SECURITY_TOTP_SECRETS = {'1': 'W55DB2NXATQAZ4AKEAS5YTIY44GEA35R'}
    SECURITY_TOTP_ISSUER = 'CRM_Concretum'
    
    RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    
    SESSION_COOKIE_SECURE = (ENV == 'production')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    WTF_CSRF_TIME_LIMIT = None
    
    SECURITY_DEBUG = True
    
class DevelopmentConfig(Config):
    DEBUG = True