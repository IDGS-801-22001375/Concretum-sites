from flask import Blueprint

clientes_bp = Blueprint('clientes', __name__, template_folder='../../templates/clientes', url_prefix='/clientes')

from . import routes