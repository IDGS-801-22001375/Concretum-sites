from flask import Blueprint

configuracion_bp = Blueprint('configuracion', __name__, template_folder='../templates/configuracion')

from . import routes