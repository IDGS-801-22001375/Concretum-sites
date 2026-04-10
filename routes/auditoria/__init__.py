from flask import Blueprint

auditoria_bp = Blueprint('auditoria', __name__, template_folder='../../templates/auditoria', url_prefix='/auditoria')

from . import routes