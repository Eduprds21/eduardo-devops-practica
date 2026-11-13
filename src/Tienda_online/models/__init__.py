"""
Paquete models
Contiene las clases del dominio: Producto, Usuario y Pedido.
"""

from .Producto import Producto, ProductoElectronico, ProductoRopa
from .Usuario import Usuario, Cliente, Administrador
from .Pedido import Pedido

__all__ = [
    "Producto",
    "ProductoElectronico",
    "ProductoRopa",
    "Usuario",
    "Cliente",
    "Administrador",
    "Pedido",
]
