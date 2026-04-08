"""
Paquete de modelos SQLAlchemy.
Importa desde aquí en cualquier parte del proyecto:

    from models import db, User, Compra, ...
"""

from .extensions    import db
from .usuarios      import Role, User, usuario_roles
from .proveedores   import Proveedor, CategoriaProveedor
from .compras       import Compra, CompraDetalle, HistorialCompra
from .pagos         import PagoProveedor
from .productos     import CategoriasProducto, Productos, Color, UnidadMedida
from .inventario    import MovimientosInventario, Existencias
from .mermas        import Merma
from .produccion    import Produccion
from .configuracion import ConfiguracionEmpresa
from .materia_prima import ExistenciaMateriaPrima, MateriaPrima
from .recetas       import RecetaDetalle, Recetas
from .comercial import VentaDetalle, Cliente, ClienteDetalle, CorteDesglose, CorteCaja, Venta

__all__ = [
    # Core
    'db',
    # Usuarios
    'Role', 'User', 'usuario_roles',
    # Proveedores
    'Proveedor', 'CategoriaProveedor',
    # Compras
    'Compra', 'CompraDetalle', 'HistorialCompra',
    # Pagos
    'PagoProveedor',
    # Productos
    'CategoriasProducto', 'Productos', 'Color', 'UnidadMedida'
    # Inventario
    'MovimientosInventario', 'Existencias'
    # Mermas
    'Merma',
    # Produccion
    'Produccion',
    # Configuración
    'ConfiguracionEmpresa',
    # Recetas
    'RecetaDetalle', 'Recetas',
    # Materia prima
    'ExistenciaMateriaPrima', 'MateriaPrima',
    # Comercial
    'VentaDetalle', 'Cliente', 'ClienteDetalle', 'CorteDesglose', 'CorteCaja', 'Venta'
]