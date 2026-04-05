from flask import Blueprint

mermas_bp = Blueprint('mermas', __name__, template_folder='../templates/mermas')

from . import routes