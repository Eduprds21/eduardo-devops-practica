"""
Archivo Principal (main.py)
Punto de entrada de la API REST de la tienda online (FastAPI).
Aquí solo se definen los endpoints: toda la lógica de negocio sigue estando en TiendaService.

Cómo arrancarla (desde esta carpeta):
    python main.py                      -> acepta conexiones de otros equipos de la red
    uvicorn main:app --reload           -> solo para este equipo (localhost)
Documentación interactiva: http://localhost:8000/docs
"""

import sys
from pathlib import Path

# Añadimos la raíz del proyecto para importar sin problemas (igual que en la práctica 1)
ruta_proyecto = Path(__file__).resolve().parent
if str(ruta_proyecto) not in sys.path:
    sys.path.insert(0, str(ruta_proyecto))

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import schemas
from Services.Tienda_service import TiendaService
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Usuario, Cliente
from models.Pedido import Pedido

app = FastAPI(title="Tienda Online API")

# Permitimos que el frontend (otra carpeta / otro puerto) llame a la API desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Un único servicio compartido por todas las peticiones (los datos viven en memoria)
tienda = TiendaService()


@app.exception_handler(RequestValidationError)
async def error_de_validacion(peticion: Request, error: RequestValidationError):
    """
    Convierte los errores de validación de Pydantic (422) al mismo formato que el resto de errores:
    {"detail": "mensaje en texto"}. Así el cliente siempre lee "detail" como una cadena.
    """
    mensajes = []
    for fallo in error.errors():
        # El primer elemento de "loc" es "body" y no aporta nada, lo quitamos
        campo = ".".join(str(parte) for parte in fallo["loc"] if parte != "body")
        texto = fallo["msg"].removeprefix("Value error, ")
        mensajes.append(f"{campo}: {texto}" if campo else texto)
    return JSONResponse(status_code=422, content={"detail": " | ".join(mensajes)})


# ---------------------------------------------------------------------------
# Funciones auxiliares: pasan los objetos del dominio a los esquemas de respuesta
# ---------------------------------------------------------------------------

def usuario_a_schema(usuario: Usuario) -> schemas.UsuarioRead:
    """Convierte un Usuario (cliente o administrador) en el esquema que se devuelve por la API."""
    return schemas.UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )


def producto_a_schema(producto: Producto) -> schemas.ProductoRead:
    """Convierte un Producto en su esquema, añadiendo los atributos propios de cada subclase."""
    datos = {
        "id": producto.id,
        "tipo": "generico",
        "nombre": producto.nombre,
        "precio": producto.precio,
        "stock": producto.stock,
    }
    # Los atributos extra solo existen en las subclases
    if isinstance(producto, ProductoElectronico):
        datos["tipo"] = "electronico"
        datos["meses_garantia"] = producto.meses_garantia
    elif isinstance(producto, ProductoRopa):
        datos["tipo"] = "ropa"
        datos["talla"] = producto.talla
        datos["color"] = producto.color
    return schemas.ProductoRead(**datos)


def pedido_a_schema(pedido: Pedido) -> schemas.PedidoRead:
    """Convierte un Pedido en su esquema, con una línea por cada producto comprado."""
    lineas = [
        schemas.PedidoItemRead(
            producto_id=producto.id,
            nombre=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=round(producto.precio * cantidad, 2),
        )
        for producto, cantidad in pedido.productos
    ]
    return schemas.PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente=usuario_a_schema(pedido.cliente),
        total=pedido.total,
        items=lineas,
    )


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

@app.post("/usuarios", response_model=schemas.UsuarioRead, status_code=201)
def crear_usuario(datos: schemas.UsuarioCreate):
    """Crea un usuario nuevo (cliente o administrador) y devuelve sus datos."""
    try:
        usuario = tienda.registrar_usuario(
            tipo=datos.tipo,
            nombre=datos.nombre,
            email=datos.email,
            direccion=datos.direccion or "",
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return usuario_a_schema(usuario)


@app.get("/usuarios", response_model=list[schemas.UsuarioRead])
def listar_usuarios():
    """Devuelve todos los usuarios registrados."""
    return [usuario_a_schema(usuario) for usuario in tienda.usuarios]


@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioRead)
def obtener_usuario(usuario_id: str):
    """Devuelve un usuario concreto, o 404 si no existe."""
    usuario = tienda.buscar_usuario_por_id(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"No existe el usuario '{usuario_id}'.")
    return usuario_a_schema(usuario)


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

@app.post("/productos", response_model=schemas.ProductoRead, status_code=201)
def crear_producto(datos: schemas.ProductoCreate):
    """Crea un producto genérico, electrónico o de ropa según el campo 'tipo'."""
    # Creamos la clase que corresponde al tipo (los campos extra ya los validó el esquema)
    if datos.tipo == "electronico":
        producto = ProductoElectronico(datos.nombre, datos.precio, datos.stock, datos.meses_garantia)
    elif datos.tipo == "ropa":
        producto = ProductoRopa(datos.nombre, datos.precio, datos.stock, datos.talla, datos.color)
    else:
        producto = Producto(datos.nombre, datos.precio, datos.stock)

    tienda.anadir_producto(producto)
    return producto_a_schema(producto)


@app.get("/productos", response_model=list[schemas.ProductoRead])
def listar_productos():
    """Devuelve todos los productos del inventario."""
    return [producto_a_schema(producto) for producto in tienda.listar_productos()]


@app.get("/productos/{producto_id}", response_model=schemas.ProductoRead)
def obtener_producto(producto_id: str):
    """Devuelve un producto concreto, o 404 si no existe."""
    producto = tienda.buscar_producto_por_id(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=f"No existe el producto '{producto_id}'.")
    return producto_a_schema(producto)


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: str):
    """Elimina un producto del inventario, o devuelve 404 si no existe."""
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(status_code=404, detail=f"No existe el producto '{producto_id}'.")
    return {"mensaje": f"Producto '{producto_id}' eliminado correctamente."}


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

@app.post("/pedidos", response_model=schemas.PedidoRead, status_code=201)
def crear_pedido(datos: schemas.PedidoCreate):
    """
    Crea un pedido para un cliente. Antes de pasarlo a TiendaService comprueba, por este orden,
    que el cliente existe (404), que es un cliente y no un administrador (400),
    que cada producto existe (404) y que hay stock suficiente (409).
    """
    cliente = tienda.buscar_usuario_por_id(datos.cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail=f"No existe el cliente '{datos.cliente_id}'.")
    if not isinstance(cliente, Cliente):
        raise HTTPException(status_code=400, detail=f"'{cliente.nombre}' no es un cliente y no puede hacer pedidos.")

    # Sumamos por producto, por si el mismo producto viene en varias líneas
    unidades_pedidas: dict[str, int] = {}
    for linea in datos.items:
        unidades_pedidas[linea.producto_id] = unidades_pedidas.get(linea.producto_id, 0) + linea.cantidad

    for producto_id, cantidad in unidades_pedidas.items():
        producto = tienda.buscar_producto_por_id(producto_id)
        if producto is None:
            raise HTTPException(status_code=404, detail=f"No existe el producto '{producto_id}'.")
        if not producto.hay_stock(cantidad):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Solicitado: {cantidad} uds | Disponible: {producto.stock} uds"
                ),
            )

    try:
        pedido = tienda.realizar_pedido(
            id_cliente=datos.cliente_id,
            productos_solicitados=list(unidades_pedidas.items()),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return pedido_a_schema(pedido)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[schemas.PedidoRead])
def listar_pedidos_de_cliente(cliente_id: str):
    """Devuelve el historial de pedidos de un usuario, del más antiguo al más reciente."""
    if tienda.buscar_usuario_por_id(cliente_id) is None:
        raise HTTPException(status_code=404, detail=f"No existe el usuario '{cliente_id}'.")
    return [pedido_a_schema(pedido) for pedido in tienda.listar_pedidos_usuario(cliente_id)]


if __name__ == "__main__":
    import uvicorn

    # host="0.0.0.0" hace que la API acepte conexiones de otros equipos de la red local
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
