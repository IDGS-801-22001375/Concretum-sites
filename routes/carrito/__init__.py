from flask import Blueprint

carrito_bp = Blueprint('carrito_bp', __name__, url_prefix='/tienda')

from . import routes