"""
Módulo Tienda_service
Contiene la capa de servicios que centraliza y gestiona las operaciones de la tienda online.
"""

import sys
from pathlib import Path

# Aseguramos que la raíz del proyecto esté en el path para facilitar las importaciones
ruta_raiz = Path(__file__).resolve().parent.parent
if str(ruta_raiz) not in sys.path:
    sys.path.insert(0, str(ruta_raiz))

from models.Producto import Producto
from models.Usuario import Usuario, Cliente, Administrador
from models.Pedido import Pedido


class TiendaService:
    """
    Servicio central de la tienda online.
    Gestiona usuarios, inventario de productos y tramitación de pedidos.
    """

    def __init__(self) -> None:
        """
        Inicializa las listas en memoria para usuarios, productos y pedidos.
        """
        self.usuarios: list[Usuario] = []
        self.productos: list[Producto] = []
        self.pedidos: list[Pedido] = []

    def registrar_usuario(
        self,
        tipo: str,
        nombre: str,
        email: str,
        direccion: str = ""
    ) -> Usuario:
        """
        Registra un nuevo usuario en la tienda (cliente o administrador).
        
        Parámetros:
            tipo (str): Tipo de usuario ('cliente' o 'administrador').
            nombre (str): Nombre completo del usuario.
            email (str): Correo electrónico del usuario.
            direccion (str, opcional): Dirección postal para clientes.
            
        Retorna:
            Usuario: La instancia del usuario registrado.
        """
        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado in ["cliente", "client"]:
            if not direccion:
                raise ValueError("Para registrar un cliente es obligatoria una dirección postal.")
            nuevo_usuario = Cliente(nombre=nombre, email=email, direccion=direccion)

        elif tipo_normalizado in ["administrador", "admin"]:
            nuevo_usuario = Administrador(nombre=nombre, email=email)

        else:
            raise ValueError(f"Tipo de usuario no válido: '{tipo}'. Debe ser 'cliente' o 'administrador'.")

        self.usuarios.append(nuevo_usuario)
        return nuevo_usuario

    def anadir_producto(self, producto: Producto) -> None:
        """
        Añade un producto al inventario de la tienda.
        
        Parámetros:
            producto (Producto): Objeto de tipo Producto o subclase a incorporar al inventario.
        """
        if not isinstance(producto, Producto):
            raise TypeError("El objeto a añadir debe ser una instancia de la clase Producto.")
        self.productos.append(producto)

    def eliminar_producto(self, id_producto: str) -> bool:
        """
        Elimina un producto del inventario a partir de su identificador único.
        
        Parámetros:
            id_producto (str): Identificador único del producto a eliminar.
            
        Retorna:
            bool: True si el producto fue encontrado y eliminado, False si no existía.
        """
        for indice, prod in enumerate(self.productos):
            if prod.id == id_producto:
                self.productos.pop(indice)
                return True
        return False

    def listar_productos(self) -> list[Producto]:
        """
        Devuelve la lista con todos los productos disponibles actualmente en el inventario.
        
        Retorna:
            list[Producto]: Lista de productos de la tienda.
        """
        return self.productos

    def buscar_usuario_por_id(self, id_usuario: str) -> Usuario | None:
        """
        Busca y retorna un usuario según su ID.
        """
        for usuario in self.usuarios:
            if usuario.id == id_usuario:
                return usuario
        return None

    def buscar_producto_por_id(self, id_producto: str) -> Producto | None:
        """
        Busca y retorna un producto según su ID.
        """
        for producto in self.productos:
            if producto.id == id_producto:
                return producto
        return None

    def realizar_pedido(
        self,
        id_cliente: str,
        productos_solicitados: list[tuple[Producto | str, int]]
    ) -> Pedido:
        """
        Tramita un nuevo pedido verificando:
        1. Que el cliente exista en el sistema y sea de tipo Cliente.
        2. Que haya stock suficiente para cada producto solicitado.
        
        Si las comprobaciones son satisfactorias:
        - Se descuenta el stock de cada producto.
        - Se genera y almacena el objeto Pedido.
        - Se retorna el pedido creado.
        
        Parámetros:
            id_cliente (str): ID del cliente que realiza la compra.
            productos_solicitados (list[tuple[Producto | str, int]]): 
                Lista de pares (producto o id_producto, cantidad).
                
        Retorna:
            Pedido: Objeto Pedido generado y confirmado.
        """
        # 1. Comprobamos que el usuario existe
        usuario = self.buscar_usuario_por_id(id_cliente)
        if usuario is None:
            raise ValueError(f"No existe ningún usuario registrado con el ID: '{id_cliente}'.")

        # Comprobamos que sea de tipo Cliente
        if not isinstance(usuario, Cliente):
            raise ValueError(f"El usuario '{usuario.nombre}' no es un cliente y no puede realizar pedidos.")

        if not productos_solicitados:
            raise ValueError("No se puede realizar un pedido sin productos.")

        # 2. Localizamos y verificamos stock de todos los productos antes de modificar nada
        lista_preparada: list[tuple[Producto, int]] = []

        for item, cantidad in productos_solicitados:
            if cantidad <= 0:
                raise ValueError(f"La cantidad solicitada debe ser mayor que 0. Recibido: {cantidad}")

            # Permite pasar tanto una instancia de Producto como el id en string
            if isinstance(item, Producto):
                producto_obj = item
            else:
                producto_obj = self.buscar_producto_por_id(str(item))

            if producto_obj is None:
                raise ValueError(f"Producto no encontrado en el inventario: '{item}'.")

            # Verificamos si hay stock suficiente
            if not producto_obj.hay_stock(cantidad):
                raise ValueError(
                    f"Stock insuficiente para '{producto_obj.nombre}'. "
                    f"Solicitado: {cantidad} uds | Disponible: {producto_obj.stock} uds"
                )

            lista_preparada.append((producto_obj, cantidad))

        # 3. Descontamos las unidades del inventario
        for producto_obj, cantidad in lista_preparada:
            producto_obj.actualizar_stock(-cantidad)

        # 4. Generamos y guardamos el pedido
        nuevo_pedido = Pedido(cliente=usuario, productos=lista_preparada)
        self.pedidos.append(nuevo_pedido)

        return nuevo_pedido

    def listar_pedidos_usuario(self, id_cliente: str) -> list[Pedido]:
        """
        Lista todos los pedidos realizados por un cliente específico,
        ordenados cronológicamente por su fecha.
        
        Parámetros:
            id_cliente (str): Identificador único del cliente.
            
        Retorna:
            list[Pedido]: Lista de pedidos del cliente ordenados por fecha.
        """
        pedidos_cliente = [pedido for pedido in self.pedidos if pedido.cliente.id == id_cliente]
        # Ordenamos por fecha de menor a mayor (orden cronológico)
        pedidos_cliente.sort(key=lambda pedido: pedido.fecha)
        return pedidos_cliente
