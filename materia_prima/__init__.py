from flask import Blueprint

materia_prima_bp = Blueprint('materia_prima', __name__, template_folder='../templates/materia_prima')

from . import routes