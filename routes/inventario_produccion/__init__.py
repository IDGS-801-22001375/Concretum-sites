from flask import Blueprint

stock_bp = Blueprint('stock_bp', __name__, url_prefix='/stock')

from . import  routes