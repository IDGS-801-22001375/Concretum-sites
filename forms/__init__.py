"""
Paquete de forms
Importa desde aquí en cualquier parte del proyecto:

    from forms import ...
"""

from .usuarios import LoginFormSimple, UsuarioForm, ExtendedRegisterForm
from .recetas import RecetaForm, RecetaDetalleForm
from .productos import ProductoForm
from .comercial import VentaForm, CorteForm
from .producciones import ProduccionForm
from .clientes import ClienteForm

__all__ = [
    'LoginFormSimple',
    'UsuarioForm',
    'ExtendedRegisterForm',
    'RecetaForm',
    'RecetaDetalleForm',
    'ProductoForm',
    'VentaForm',
    'CorteForm',
    'ProduccionForm',
    'ClienteForm'
]