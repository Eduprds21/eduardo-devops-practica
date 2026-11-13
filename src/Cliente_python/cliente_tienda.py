"""
Cliente Python de la API de la tienda online.
Es independiente del servidor: no importa TiendaService ni los modelos, todo va por HTTP con requests.

Uso:
    python cliente_tienda.py                          -> usa BASE_URL (localhost)
    python cliente_tienda.py http://192.168.1.34:8000 -> usa la IP de otro equipo
"""

import sys

import requests

# Dirección de la API. Para probar con otro equipo basta con cambiarla aquí
# o pasarla como primer argumento al ejecutar el script.
BASE_URL = "http://localhost:8000"
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1].rstrip("/")


def hacer_peticion(metodo: str, ruta: str, codigo_esperado: int, **kwargs):
    """
    Lanza una petición a la API, comprueba el código de estado y devuelve el JSON recibido.
    Si el código no es el esperado, muestra el motivo y detiene el script.

    Parámetros:
        metodo: "GET", "POST", "DELETE"...
        ruta: parte final de la URL, por ejemplo "/usuarios".
        codigo_esperado: código HTTP que debería devolver la API si todo va bien.
        **kwargs: por ejemplo json=... con el cuerpo de la petición.
    """
    url = BASE_URL + ruta
    respuesta = requests.request(metodo, url, timeout=10, **kwargs)

    if respuesta.status_code == codigo_esperado:
        print(f"[OK] {metodo} {ruta} -> {respuesta.status_code}")
        return respuesta.json()

    # Algo ha ido mal: las respuestas de error de FastAPI traen el motivo en "detail"
    print(f"[ERROR] {metodo} {ruta} -> {respuesta.status_code} (esperado {codigo_esperado})")
    try:
        print(f"        Motivo: {respuesta.json().get('detail')}")
    except ValueError:
        print(f"        Respuesta recibida: {respuesta.text[:200]}")
    sys.exit(1)


def main() -> None:
    print(f"\nProbando la API en {BASE_URL}\n")

    # 1. Crear un usuario (cliente)
    print("--- 1. Crear un usuario ---")
    cliente = hacer_peticion("POST", "/usuarios", 201, json={
        "nombre": "Lucía Fernández",
        "email": "lucia.fernandez@correo.es",
        "tipo": "cliente",
        "direccion": "Calle Mayor 14, 3ºB, Madrid",
    })
    print(f"      Creado: {cliente['nombre']} (id {cliente['id']})\n")

    # 2. Consultar la lista de usuarios
    print("--- 2. Lista de usuarios ---")
    usuarios = hacer_peticion("GET", "/usuarios", 200)
    for usuario in usuarios:
        rol = "ADMIN" if usuario["es_admin"] else "cliente"
        print(f"      {usuario['id']} | {usuario['nombre']} | {usuario['email']} | {rol}")
    print()

    # 3. Crear varios productos (uno de cada tipo)
    print("--- 3. Crear productos ---")
    smartphone = hacer_peticion("POST", "/productos", 201, json={
        "tipo": "electronico",
        "nombre": "Smartphone Galaxy S24",
        "precio": 799.99,
        "stock": 10,
        "meses_garantia": 36,
    })
    sudadera = hacer_peticion("POST", "/productos", 201, json={
        "tipo": "ropa",
        "nombre": "Sudadera Capucha Urban",
        "precio": 39.95,
        "stock": 20,
        "talla": "L",
        "color": "Azul Marino",
    })
    hacer_peticion("POST", "/productos", 201, json={
        "tipo": "generico",
        "nombre": "Botella reutilizable",
        "precio": 9.5,
        "stock": 50,
    })
    print()

    # 4. Consultar la lista de productos
    print("--- 4. Lista de productos ---")
    productos = hacer_peticion("GET", "/productos", 200)
    for producto in productos:
        print(f"      {producto['id']} | {producto['tipo']} | {producto['nombre']} | "
              f"{producto['precio']:.2f}€ | stock {producto['stock']}")
    print()

    # 5. Crear un pedido para el usuario
    print("--- 5. Crear un pedido ---")
    pedido = hacer_peticion("POST", "/pedidos", 201, json={
        "cliente_id": cliente["id"],
        "items": [
            {"producto_id": smartphone["id"], "cantidad": 1},
            {"producto_id": sudadera["id"], "cantidad": 2},
        ],
    })
    print(f"      Pedido {pedido['id']} creado, total {pedido['total']:.2f}€\n")

    # 6. Consultar los pedidos del usuario
    print("--- 6. Pedidos del usuario ---")
    pedidos = hacer_peticion("GET", f"/usuarios/{cliente['id']}/pedidos", 200)
    for pedido_cliente in pedidos:
        print(f"      Pedido {pedido_cliente['id']} | {pedido_cliente['fecha']} | "
              f"total {pedido_cliente['total']:.2f}€")
        for linea in pedido_cliente["items"]:
            print(f"         - {linea['nombre']} x {linea['cantidad']} = {linea['subtotal']:.2f}€")
    print()

    # Extra: comprobamos que la API rechaza peticiones incorrectas con el código adecuado
    print("--- Extra. Errores esperados ---")
    hacer_peticion("POST", "/pedidos", 409, json={
        "cliente_id": cliente["id"],
        "items": [{"producto_id": smartphone["id"], "cantidad": 500}],
    })
    hacer_peticion("GET", "/usuarios/noexiste", 404)
    print()


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"No se pudo conectar con la API en {BASE_URL}. ¿Está arrancada y la dirección es correcta?")
