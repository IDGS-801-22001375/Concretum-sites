"""
Paquete de modelos SQLAlchemy.
Importa desde aquí en cualquier parte del proyecto:

    from models import db, User, Compra, ...
"""

from .extensions          import db
from .usuarios      import Role, User, usuario_roles
from .proveedores   import Proveedor, CategoriaProveedor
from .compras       import Compra, CompraDetalle, HistorialCompra
from .pagos         import PagoProveedor
from .materia_prima import MateriaPrima, ExistenciaMateriaPrima
from .productos     import CategoriaProducto, Producto, Existencia
from .inventario    import MovimientoInventario
from .produccion    import Receta, Produccion
from .mermas        import Merma
from .configuracion import ConfiguracionEmpresa
 
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
    # Materia Prima
    'MateriaPrima', 'ExistenciaMateriaPrima',
    # Productos
    'CategoriaProducto', 'Producto', 'Existencia',
    # Inventario
    'MovimientoInventario',
    # Producción
    'Receta', 'Produccion',
    # Mermas
    'Merma',
    # Configuración
    'ConfiguracionEmpresa',
]