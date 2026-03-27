import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY", "Clave secreta")
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:,vL&W}Z9dBXLJYjGGpux]itZ;-GNea_wgC{G}4Z6,gHX}.*hWh@127.0.0.1:3306/crm_fabrica?charset=utf8mb4",
    )
