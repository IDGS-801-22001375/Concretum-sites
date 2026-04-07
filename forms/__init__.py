"""
Paquete de forms
Importa desde aquí en cualquier parte del proyecto:

    from models import db, User, Compra, ...
"""

from .usuarios import LoginFormSimple, UsuarioForm
from .recetas import RecetaForm, RecetaDetalleForm
from .productos import ProductoForm
from .comercial import VentaForm, CorteForm, TicketForm

__all__ = [
    'LoginFormSimple',
    'UsuarioForm',
    'RecetaForm',
    'RecetaDetalleForm',
    'ProductoForm',
    'VentaForm',
    'CorteForm',
    'TicketForm'
]