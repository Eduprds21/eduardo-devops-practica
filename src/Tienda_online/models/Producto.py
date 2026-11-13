"""
Módulo Producto
Define la clase base Producto y sus subclases especializadas ProductoElectronico y ProductoRopa.
"""

import uuid


class Producto:
    """
    Clase padre que representa un producto general en la tienda online.
    
    Atributos:
        id (str): Identificador único generado automáticamente.
        nombre (str): Nombre del producto.
        precio (float): Precio unitario en euros.
        stock (int): Unidades disponibles en el almacén.
    """

    def __init__(self, nombre: str, precio: float, stock: int = 0) -> None:
        """
        Inicializa un nuevo producto con un identificador único automático.
        """
        # Generamos un identificador único y corto usando uuid4
        self.id: str = str(uuid.uuid4())[:8]
        self.nombre: str = nombre
        self.precio: float = float(precio)
        self.stock: int = int(stock)

    def hay_stock(self, cantidad: int) -> bool:
        """
        Comprueba si hay suficiente stock disponible para la cantidad solicitada.
        
        Parámetros:
            cantidad (int): Número de unidades requeridas.
            
        Retorna:
            bool: True si hay suficiente stock, False en caso contrario.
        """
        return cantidad > 0 and self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """
        Actualiza el stock del producto sumando o restando unidades.
        
        Parámetros:
            cantidad (int): Unidades a modificar. 
                            Valor positivo para reposición de inventario.
                            Valor negativo para compras/salidas.
        """
        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            raise ValueError(
                f"No hay suficiente stock de '{self.nombre}'. "
                f"Stock actual: {self.stock}, unidades a retirar: {-cantidad}"
            )
        self.stock = nuevo_stock

    def __str__(self) -> str:
        """
        Devuelve una cadena legible con las características principales del producto.
        """
        return (
            f"[ID: {self.id}] {self.nombre} | "
            f"Precio: {self.precio:.2f}€ | "
            f"Stock: {self.stock} uds"
        )


class ProductoElectronico(Producto):
    """
    Subclase de Producto para artículos electrónicos, con información de garantía.
    
    Atributos adicionales:
        meses_garantia (int): Período de garantía en meses.
    """

    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int) -> None:
        """
        Inicializa un producto electrónico heredando los atributos base y añadiendo la garantía.
        """
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = int(meses_garantia)

    def __str__(self) -> str:
        """
        Sobrescribe __str__ para incluir la información de la garantía.
        """
        return (
            f"[ID: {self.id}] [Electrónica] {self.nombre} | "
            f"Precio: {self.precio:.2f}€ | "
            f"Stock: {self.stock} uds | "
            f"Garantía: {self.meses_garantia} meses"
        )


class ProductoRopa(Producto):
    """
    Subclase de Producto para prendas de ropa, con información de talla y color.
    
    Atributos adicionales:
        talla (str): Talla de la prenda (por ejemplo: 'S', 'M', 'L', 'XL').
        color (str): Color de la prenda.
    """

    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str) -> None:
        """
        Inicializa un producto de ropa heredando los atributos base y añadiendo talla y color.
        """
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        """
        Sobrescribe __str__ para incluir la talla y el color de la prenda.
        """
        return (
            f"[ID: {self.id}] [Ropa] {self.nombre} | "
            f"Precio: {self.precio:.2f}€ | "
            f"Stock: {self.stock} uds | "
            f"Talla: {self.talla} | Color: {self.color}"
        )
