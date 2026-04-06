from flask import Blueprint

proveedores_bp = Blueprint('proveedores_bp', __name__)

from . import routes