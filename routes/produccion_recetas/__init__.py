from flask import Blueprint

produccion_recetas_bp = Blueprint('produccion_recetas_bp', __name__, url_prefix='/produccion-rectas')

from . import  routes