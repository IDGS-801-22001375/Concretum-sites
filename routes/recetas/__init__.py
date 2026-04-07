from flask import Blueprint

recetas_bp = Blueprint('recetas_bp', __name__, url_prefix='/produccion')

from . import  routes