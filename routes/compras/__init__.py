from flask import Blueprint

compras_bp = Blueprint('compras', __name__, template_folder='../templates/compras')

from . import routes