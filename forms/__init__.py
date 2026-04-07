"""
Paquete de forms
Importa desde aquí en cualquier parte del proyecto:

    from models import db, User, Compra, ...
"""

from .usuarios import LoginFormSimple, UsuarioForm
from .recetas import RecetaForm, RecetaDetalleForm
from .productos import ProductoForm

__all__ = [
    'LoginFormSimple',
    'UsuarioForm',
    'RecetaForm',
    'RecetaDetalleForm',
    'ProductoForm'
]