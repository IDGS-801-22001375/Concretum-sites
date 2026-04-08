"""
Paquete de forms
Importa desde aquí en cualquier parte del proyecto:

    from models import db, User, Compra, ...
"""

from .usuarios import LoginFormSimple, UsuarioForm, ExtendedRegisterForm
from .recetas import RecetaForm, RecetaDetalleForm
from .productos import ProductoForm
from .comercial import VentaForm, CorteForm, TicketForm
from .clientes import ClienteForm

__all__ = [
    'LoginFormSimple', 'UsuarioForm','ExtendedRegisterForm', 'RecetaForm', 'RecetaDetalleForm',
    'ProductoForm', 'VentaForm', 'CorteForm', 'TicketForm', 'ClienteForm'
]