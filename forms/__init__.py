"""
Paquete de forms
Importa desde aquí en cualquier parte del proyecto:

    from forms import ...
"""

from .usuarios import LoginFormSimple, UsuarioForm, ExtendedRegisterForm
from .recetas import RecetaForm, RecetaDetalleForm
from .productos import ProductoForm
from .comercial import VentaForm, CorteForm, TicketForm
from .producciones import ProduccionForm
from .clientes import ClienteForm
from .carrito import AgregarAlCarritoForm, ActualizarCantidadForm, CheckoutForm, ContactoClienteForm

__all__ = [
    'LoginFormSimple',
    'UsuarioForm',
    'ExtendedRegisterForm',
    'RecetaForm',
    'RecetaDetalleForm',
    'ProductoForm',
    'VentaForm',
    'CorteForm',
    'TicketForm',
    'ProduccionForm',
    'ClienteForm'
    'AgregarAlCarritoForm', 
    'ActualizarCantidadForm', 
    'CheckoutForm', 
    'ContactoClienteForm'
]