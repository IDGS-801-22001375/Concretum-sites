from flask import Blueprint

comercial_bp = Blueprint('comercial_bp', __name__, url_prefix='/comercial')

from . import routes