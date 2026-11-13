"""
Módulo schemas
Esquemas Pydantic de la API: definen qué datos recibimos del cliente (peticiones)
y qué datos le devolvemos (respuestas). FastAPI los usa para validar y para generar /docs.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

class UsuarioCreate(BaseModel):
    """Datos necesarios para crear un usuario."""
    nombre: str = Field(min_length=1)
    # Comprobación sencilla de email (algo@dominio.ext), sin dependencias extra
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    tipo: Literal["cliente", "administrador"]
    direccion: str | None = None  # Solo es obligatoria para los clientes

    @model_validator(mode="after")
    def comprobar_direccion_de_cliente(self):
        if self.tipo == "cliente" and not self.direccion:
            raise ValueError("Un cliente necesita una dirección postal.")
        return self


class UsuarioRead(BaseModel):
    """Datos de un usuario que se devuelven al cliente."""
    id: str
    nombre: str
    email: str
    es_admin: bool


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

class ProductoCreate(BaseModel):
    """
    Datos para crear un producto. Según el tipo hay que rellenar unos campos u otros:
    - generico: solo los campos básicos.
    - electronico: además meses_garantia.
    - ropa: además talla y color.
    """
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    meses_garantia: int | None = Field(default=None, ge=0)
    talla: str | None = None
    color: str | None = None

    @model_validator(mode="after")
    def comprobar_atributos_del_tipo(self):
        if self.tipo == "electronico" and self.meses_garantia is None:
            raise ValueError("Un producto electrónico necesita 'meses_garantia'.")
        if self.tipo == "ropa" and not (self.talla and self.color):
            raise ValueError("Un producto de ropa necesita 'talla' y 'color'.")
        return self


class ProductoRead(BaseModel):
    """Datos de un producto que se devuelven al cliente (los opcionales dependen del tipo)."""
    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

class PedidoItemCreate(BaseModel):
    """Una línea del pedido que se quiere crear: qué producto y cuántas unidades."""
    producto_id: str
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    """Datos para crear un pedido: el cliente y las líneas que compra."""
    cliente_id: str
    items: list[PedidoItemCreate] = Field(min_length=1)


class PedidoItemRead(BaseModel):
    """Una línea de un pedido ya creado."""
    producto_id: str
    nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoRead(BaseModel):
    """Pedido completo tal y como se devuelve al cliente."""
    id: str
    fecha: datetime
    cliente: UsuarioRead
    total: float
    items: list[PedidoItemRead]
