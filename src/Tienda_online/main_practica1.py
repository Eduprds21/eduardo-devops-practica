"""
Archivo Principal (main.py)
Punto de entrada de la aplicación para probar el funcionamiento de la tienda online.
Realiza las pruebas manuales solicitadas en la práctica:
1. Instanciar TiendaService.
2. Registrar 3 clientes y 1 administrador.
3. Crear 5 productos de diferentes categorías y añadirlos al inventario.
4. Listar productos para verificar el inventario.
5. Simular 3 pedidos realizados por distintos clientes con varios productos.
6. Consultar el historial de pedidos de un cliente.
7. Mostrar los pedidos en consola y el stock actualizado de los productos.
"""

import sys
from pathlib import Path

# Añadimos la raíz del proyecto para importar sin problemas
ruta_proyecto = Path(__file__).resolve().parent
if str(ruta_proyecto) not in sys.path:
    sys.path.insert(0, str(ruta_proyecto))

from Services.Tienda_service import TiendaService
from models.Producto import ProductoElectronico, ProductoRopa


def main() -> None:
    print("\n" + "=" * 70)
    print(" INICIO DE LA SIMULACIÓN - SISTEMA DE TIENDA ONLINE")
    print("=" * 70 + "\n")

    # 1. Crear una instancia del servicio central
    print("[1] Creando el servicio central de la tienda...")
    tienda = TiendaService()
    print(" -> TiendaService inicializado correctamente.\n")

    # 2. Registrar al menos tres clientes y un administrador
    print("[2] Registrando usuarios en la tienda...")
    cliente_lucia = tienda.registrar_usuario(
        tipo="cliente",
        nombre="Lucía Fernández",
        email="lucia.fernandez@correo.es",
        direccion="Calle Mayor 14, 3ºB, Madrid"
    )
    cliente_marcos = tienda.registrar_usuario(
        tipo="cliente",
        nombre="Marcos Gómez",
        email="marcos.gomez@correo.es",
        direccion="Avenida del Puerto 45, Valencia"
    )
    cliente_elena = tienda.registrar_usuario(
        tipo="cliente",
        nombre="Elena Ramos",
        email="elena.ramos@correo.es",
        direccion="Paseo de Gracia 102, Barcelona"
    )
    administrador_carlos = tienda.registrar_usuario(
        tipo="administrador",
        nombre="Carlos Vega",
        email="carlos.admin@tiendaonline.com"
    )

    print("Usuarios registrados con éxito:")
    for usuario in tienda.usuarios:
        tipo_rol = "ADMINISTRADOR" if usuario.is_admin() else "CLIENTE"
        print(f"   • [{tipo_rol}] {usuario}")
    print()

    # 3. Crear cinco productos de diferentes categorías y añadirlos al inventario
    print("[3] Creando 5 productos y añadiéndolos al inventario...")
    
    # Productos de la categoría Electrónica (con meses de garantía)
    smartphone = ProductoElectronico(
        nombre="Smartphone Galaxy S24",
        precio=799.99,
        stock=10,
        meses_garantia=36
    )
    auriculares = ProductoElectronico(
        nombre="Auriculares Bluetooth Sony",
        precio=89.50,
        stock=15,
        meses_garantia=24
    )
    teclado = ProductoElectronico(
        nombre="Teclado Mecánico Inalámbrico",
        precio=65.00,
        stock=12,
        meses_garantia=12
    )

    # Productos de la categoría Ropa (con talla y color)
    sudadera = ProductoRopa(
        nombre="Sudadera Capucha Urban",
        precio=39.95,
        stock=20,
        talla="L",
        color="Azul Marino"
    )
    pantalon = ProductoRopa(
        nombre="Pantalón Vaquero Slim",
        precio=49.99,
        stock=18,
        talla="M",
        color="Negro"
    )

    # Añadimos los productos a la tienda
    for producto in [smartphone, auriculares, teclado, sudadera, pantalon]:
        tienda.anadir_producto(producto)
    print(" -> Se han añadido 5 productos al inventario (3 de electrónica y 2 de ropa).\n")

    # 4. Listar los productos para comprobar que el inventario se ha llenado correctamente
    print("[4] Listando catálogo inicial disponible en el inventario:")
    print("-" * 70)
    for prod in tienda.listar_productos():
        print(f"   {prod}")
    print("-" * 70 + "\n")

    # 5. Simular tres pedidos realizados por distintos clientes con varios productos
    print("[5] Simulando compras (3 pedidos)...")
    
    # Pedido 1: Lucía compra 1 Smartphone y 2 Sudaderas
    print("\n Tramitando Pedido 1 (Cliente: Lucía Fernández)...")
    pedido_1 = tienda.realizar_pedido(
        id_cliente=cliente_lucia.id,
        productos_solicitados=[
            (smartphone, 1),
            (sudadera, 2)
        ]
    )
    print(pedido_1)

    # Pedido 2: Marcos compra 2 Auriculares Bluetooth y 1 Pantalón Vaquero
    print("\n Tramitando Pedido 2 (Cliente: Marcos Gómez)...")
    pedido_2 = tienda.realizar_pedido(
        id_cliente=cliente_marcos.id,
        productos_solicitados=[
            (auriculares, 2),
            (pantalon, 1)
        ]
    )
    print(pedido_2)

    # Pedido 3: Elena compra 1 Teclado Mecánico y 1 Sudadera
    print("\n Tramitando Pedido 3 (Cliente: Elena Ramos)...")
    pedido_3 = tienda.realizar_pedido(
        id_cliente=cliente_elena.id,
        productos_solicitados=[
            (teclado, 1),
            (sudadera, 1)
        ]
    )
    print(pedido_3)

    # Añadimos un pedido extra para Lucía para probar de forma rica el historial cronológico
    print("\n Tramitando Pedido Adicional de Lucía para enriquecer su historial...")
    pedido_4 = tienda.realizar_pedido(
        id_cliente=cliente_lucia.id,
        productos_solicitados=[
            (auriculares, 1),
            (pantalon, 2)
        ]
    )
    print(pedido_4)

    # 6. Comprobar el histórico de pedidos de un cliente
    print("\n" + "=" * 70)
    print(f"[6] Histórico de pedidos del cliente: {cliente_lucia.nombre} (ID: {cliente_lucia.id})")
    print("=" * 70)
    historial_lucia = tienda.listar_pedidos_usuario(cliente_lucia.id)
    print(f"Número de pedidos encontrados: {len(historial_lucia)}\n")
    
    for num, pedido in enumerate(historial_lucia, start=1):
        print(f"--- Historial Pedido #{num} ---")
        print(pedido)
        print()

    # 7. Mostrar el stock actualizado de los productos tras todas las compras
    print("=" * 70)
    print("[7] STOCK ACTUALIZADO DEL INVENTARIO TRAS LAS COMPRAS REALIZADAS:")
    print("=" * 70)
    for prod in tienda.listar_productos():
        print(f"   {prod}")
    print("=" * 70 + "\n")

    # Prueba extra: verificación de control de stock insuficiente
    print("[Control de Stock] Comprobando intento de compra que supera el stock disponible:")
    try:
        tienda.realizar_pedido(
            id_cliente=cliente_marcos.id,
            productos_solicitados=[(smartphone, 50)]  # Solo quedan 9
        )
    except ValueError as error_stock:
        print(f" -> Validación correcta: El sistema impidió la compra por falta de stock:")
        print(f"    '{error_stock}'")

    print("\n" + "=" * 70)
    print(" TODAS LAS COMPROBACIONES SE HAN COMPLETADO SATISFACTORIAMENTE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
