"""
Módulo Pedido
Define la clase Pedido para registrar las compras de los clientes con sus productos y totales.
"""

from datetime import datetime
import uuid
from models.Producto import Producto
from models.Usuario import Cliente


class Pedido:
    """
    Representa una compra efectuada por un cliente en la tienda online.
    
    Atributos:
        id (str): Identificador único del pedido.
        cliente (Cliente): Cliente que ha realizado la compra.
        productos (list[tuple[Producto, int]]): Lista de tuplas con el producto y la cantidad comprada.
        fecha (datetime): Fecha y hora en la que se generó el pedido.
        total (float): Importe total del pedido en euros.
    """

    def __init__(
        self,
        cliente: Cliente,
        productos: list[tuple[Producto, int]],
        id_pedido: str | None = None,
        fecha: datetime | None = None,
    ) -> None:
        """
        Inicializa un pedido con el cliente, productos adquiridos y calcula su total.
        """
        self.id: str = id_pedido if id_pedido else str(uuid.uuid4())[:8]
        self.cliente: Cliente = cliente
        self.productos: list[tuple[Producto, int]] = productos
        self.fecha: datetime = fecha if fecha else datetime.now()
        # Calculamos el total al momento de construir el pedido
        self.total: float = self.calcular_total()

    def calcular_total(self) -> float:
        """
        Calcula el importe total de la compra multiplicando el precio de cada producto por su cantidad.
        
        Retorna:
            float: Importe total redondeado a 2 decimales.
        """
        importe_total = 0.0
        for producto, cantidad in self.productos:
            importe_total += producto.precio * cantidad
        return round(importe_total, 2)

    def __str__(self) -> str:
        """
        Devuelve un resumen legible del pedido con el cliente, los artículos y el total a pagar.
        """
        fecha_texto = self.fecha.strftime("%d/%m/%Y %H:%M:%S")
        resumen = [
            f"==================================================",
            f" PEDIDO #{self.id} | Fecha: {fecha_texto}",
            f" Cliente: {self.cliente.nombre} ({self.cliente.email})",
            f" Dirección de entrega: {self.cliente.direccion}",
            f"--------------------------------------------------",
            f" Artículos comprados:"
        ]
        
        for producto, cantidad in self.productos:
            subtotal = producto.precio * cantidad
            resumen.append(f"   * {producto.nombre} x {cantidad} ud(s) -> {subtotal:.2f}€ ({producto.precio:.2f}€/ud)")
            
        resumen.append(f"--------------------------------------------------")
        resumen.append(f" TOTAL DE LA COMPRA: {self.total:.2f}€")
        resumen.append(f"==================================================")
        
        return "\n".join(resumen)
