// Frontend de la tienda online.
// Todo lo que sale hacia el servidor pasa por la función llamarApi(), así que
// ahí es donde se ve cada petición HTTP. Cada función de abajo indica qué endpoint usa.

// ---------------------------------------------------------------------------
// Comunicación con la API
// ---------------------------------------------------------------------------

const campoUrl = document.getElementById("urlApi");

// Recordamos la última dirección usada para no tener que escribirla cada vez
campoUrl.value = localStorage.getItem("urlApi") || campoUrl.value;

// Hace una petición HTTP a la API y devuelve el JSON de la respuesta.
// Si el servidor responde con un error (404, 409, 422...) lanza una excepción con su mensaje.
async function llamarApi(ruta, opciones = {}) {
  const urlBase = campoUrl.value.replace(/\/$/, "");
  const respuesta = await fetch(urlBase + ruta, opciones);
  const datos = await respuesta.json();

  if (!respuesta.ok) {
    throw new Error(textoDeError(datos.detail));
  }
  return datos;
}

// La API devuelve siempre el motivo del error como texto en "detail" (404, 409, 422...)
function textoDeError(detalle) {
  return detalle || "Error desconocido";
}

// Opciones de fetch para enviar un cuerpo JSON
function opcionesJson(metodo, cuerpo) {
  return {
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  };
}

// ---------------------------------------------------------------------------
// Utilidades de la pantalla
// ---------------------------------------------------------------------------

const cajaMensaje = document.getElementById("mensaje");

function mostrarMensaje(texto, esError = false) {
  cajaMensaje.textContent = texto;
  cajaMensaje.className = "mensaje " + (esError ? "error" : "ok");
}

// Evita que un nombre con símbolos como < o & rompa el HTML
function escapar(texto) {
  const auxiliar = document.createElement("div");
  auxiliar.textContent = texto;
  return auxiliar.innerHTML;
}

function formatoEuros(importe) {
  return importe.toFixed(2) + " €";
}

// Estado en memoria del frontend: los datos cargados y las líneas del pedido en preparación
let listaProductos = [];
let listaUsuarios = [];
let lineasPedido = [];

// ---------------------------------------------------------------------------
// Productos
// ---------------------------------------------------------------------------

// GET /productos -> lista de productos
async function cargarProductos() {
  listaProductos = await llamarApi("/productos");
  pintarProductos();
  rellenarSelectProductos();
}

function pintarProductos() {
  const cuerpoTabla = document.getElementById("tablaProductos");
  cuerpoTabla.innerHTML = listaProductos.map((producto) => {
    // Los detalles dependen del tipo de producto
    let detalles = "";
    if (producto.tipo === "electronico") detalles = producto.meses_garantia + " meses de garantía";
    if (producto.tipo === "ropa") detalles = "Talla " + producto.talla + ", " + producto.color;

    return `<tr>
      <td>${escapar(producto.id)}</td>
      <td>${producto.tipo}</td>
      <td>${escapar(producto.nombre)}</td>
      <td>${formatoEuros(producto.precio)}</td>
      <td>${producto.stock}</td>
      <td>${escapar(detalles)}</td>
      <td><button class="peligro" onclick="eliminarProducto('${producto.id}')">Eliminar</button></td>
    </tr>`;
  }).join("");
}

// POST /productos -> crea un producto
async function crearProducto(evento) {
  evento.preventDefault();
  const tipo = document.getElementById("productoTipo").value;

  const producto = {
    tipo: tipo,
    nombre: document.getElementById("productoNombre").value,
    precio: parseFloat(document.getElementById("productoPrecio").value),
    stock: parseInt(document.getElementById("productoStock").value),
  };
  // Solo enviamos los campos extra que corresponden al tipo elegido
  if (tipo === "electronico") {
    producto.meses_garantia = parseInt(document.getElementById("productoGarantia").value);
  }
  if (tipo === "ropa") {
    producto.talla = document.getElementById("productoTalla").value;
    producto.color = document.getElementById("productoColor").value;
  }

  try {
    const creado = await llamarApi("/productos", opcionesJson("POST", producto));
    mostrarMensaje(`Producto '${creado.nombre}' creado con id ${creado.id}.`);
    document.getElementById("formProducto").reset();
    mostrarCamposDelTipo();
    await cargarProductos();
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

// DELETE /productos/{id} -> elimina un producto
async function eliminarProducto(idProducto) {
  try {
    const respuesta = await llamarApi("/productos/" + idProducto, { method: "DELETE" });
    mostrarMensaje(respuesta.mensaje);
    await cargarProductos();
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

// Enseña u oculta los campos extra del formulario según el tipo de producto
function mostrarCamposDelTipo() {
  const tipo = document.getElementById("productoTipo").value;
  document.querySelectorAll(".campo-electronico").forEach((campo) => {
    campo.classList.toggle("oculto", tipo !== "electronico");
    campo.required = tipo === "electronico";
  });
  document.querySelectorAll(".campo-ropa").forEach((campo) => {
    campo.classList.toggle("oculto", tipo !== "ropa");
    campo.required = tipo === "ropa";
  });
}

// ---------------------------------------------------------------------------
// Usuarios
// ---------------------------------------------------------------------------

// GET /usuarios -> lista de usuarios
async function cargarUsuarios() {
  listaUsuarios = await llamarApi("/usuarios");
  pintarUsuarios();
  rellenarSelectsDeUsuarios();
}

function pintarUsuarios() {
  const cuerpoTabla = document.getElementById("tablaUsuarios");
  cuerpoTabla.innerHTML = listaUsuarios.map((usuario) => `<tr>
    <td>${escapar(usuario.id)}</td>
    <td>${escapar(usuario.nombre)}</td>
    <td>${escapar(usuario.email)}</td>
    <td>${usuario.es_admin ? "Administrador" : "Cliente"}</td>
  </tr>`).join("");
}

// POST /usuarios -> crea un usuario
async function crearUsuario(evento) {
  evento.preventDefault();
  const usuario = {
    tipo: document.getElementById("usuarioTipo").value,
    nombre: document.getElementById("usuarioNombre").value,
    email: document.getElementById("usuarioEmail").value,
    direccion: document.getElementById("usuarioDireccion").value || null,
  };

  try {
    const creado = await llamarApi("/usuarios", opcionesJson("POST", usuario));
    mostrarMensaje(`Usuario '${creado.nombre}' creado con id ${creado.id}.`);
    document.getElementById("formUsuario").reset();
    await cargarUsuarios();
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

// Rellena los desplegables de "crear pedido" y "consultar pedidos"
function rellenarSelectsDeUsuarios() {
  // Para comprar solo valen los clientes; para consultar pedidos, cualquier usuario
  const soloClientes = listaUsuarios.filter((usuario) => !usuario.es_admin);
  const opcion = (usuario) => `<option value="${usuario.id}">${escapar(usuario.nombre)} (${usuario.id})</option>`;

  // Guardamos lo que estaba elegido para no perderlo al refrescar las listas
  const clienteElegido = document.getElementById("pedidoCliente").value;
  const usuarioElegido = document.getElementById("consultaUsuario").value;

  document.getElementById("pedidoCliente").innerHTML = soloClientes.map(opcion).join("");
  document.getElementById("consultaUsuario").innerHTML = listaUsuarios.map(opcion).join("");

  document.getElementById("pedidoCliente").value = clienteElegido;
  document.getElementById("consultaUsuario").value = usuarioElegido;
}

// ---------------------------------------------------------------------------
// Pedidos
// ---------------------------------------------------------------------------

function rellenarSelectProductos() {
  const desplegable = document.getElementById("pedidoProducto");
  const seleccionado = desplegable.value; // para no perder el producto elegido al refrescar

  desplegable.innerHTML = listaProductos
    .map((producto) => `<option value="${producto.id}">${escapar(producto.nombre)} (stock ${producto.stock})</option>`)
    .join("");
  desplegable.value = seleccionado;
}

// Añade una línea (producto + cantidad) al pedido que se está preparando
function anadirLinea() {
  const productoId = document.getElementById("pedidoProducto").value;
  const cantidad = parseInt(document.getElementById("pedidoCantidad").value);
  if (!productoId || !(cantidad > 0)) {
    mostrarMensaje("Elige un producto y una cantidad mayor que 0.", true);
    return;
  }
  lineasPedido.push({ producto_id: productoId, cantidad: cantidad });
  pintarLineas();
}

function pintarLineas() {
  document.getElementById("lineasPedido").innerHTML = lineasPedido.map((linea) => {
    const producto = listaProductos.find((p) => p.id === linea.producto_id);
    const nombre = producto ? producto.nombre : linea.producto_id;
    return `<li>${escapar(nombre)} x ${linea.cantidad}</li>`;
  }).join("");
}

// POST /pedidos -> crea el pedido con las líneas añadidas
async function enviarPedido() {
  const clienteId = document.getElementById("pedidoCliente").value;
  if (!clienteId) {
    mostrarMensaje("Primero hace falta crear algún cliente.", true);
    return;
  }

  try {
    const pedido = await llamarApi("/pedidos", opcionesJson("POST", {
      cliente_id: clienteId,
      items: lineasPedido,
    }));
    mostrarMensaje(`Pedido ${pedido.id} creado. Total: ${formatoEuros(pedido.total)}.`);
    lineasPedido = [];
    pintarLineas();
    await cargarProductos(); // el stock ha cambiado
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

// GET /usuarios/{id}/pedidos -> pedidos de un usuario
async function consultarPedidos() {
  const usuarioId = document.getElementById("consultaUsuario").value;
  if (!usuarioId) {
    mostrarMensaje("No hay usuarios para consultar.", true);
    return;
  }

  try {
    const pedidos = await llamarApi(`/usuarios/${usuarioId}/pedidos`);
    const caja = document.getElementById("resultadoPedidos");

    if (pedidos.length === 0) {
      caja.innerHTML = "<p>Este usuario todavía no tiene pedidos.</p>";
      return;
    }
    caja.innerHTML = pedidos.map((pedido) => `<div class="pedido">
      <strong>Pedido ${escapar(pedido.id)}</strong> - ${new Date(pedido.fecha).toLocaleString("es-ES")}
      <ul>${pedido.items.map((linea) =>
        `<li>${escapar(linea.nombre)} x ${linea.cantidad} = ${formatoEuros(linea.subtotal)}</li>`).join("")}</ul>
      <strong>Total: ${formatoEuros(pedido.total)}</strong>
    </div>`).join("");
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

// ---------------------------------------------------------------------------
// Arranque
// ---------------------------------------------------------------------------

// Carga productos y usuarios desde la API (se usa al abrir la página y al cambiar de servidor)
async function cargarTodo() {
  try {
    await cargarProductos();
    await cargarUsuarios();
    mostrarMensaje("Conectado con " + campoUrl.value);
  } catch (error) {
    mostrarMensaje("No se pudo conectar con la API: " + error.message, true);
  }
}

document.getElementById("botonConectar").addEventListener("click", () => {
  localStorage.setItem("urlApi", campoUrl.value);
  cargarTodo();
});
document.getElementById("productoTipo").addEventListener("change", mostrarCamposDelTipo);
document.getElementById("formProducto").addEventListener("submit", crearProducto);
document.getElementById("formUsuario").addEventListener("submit", crearUsuario);
document.getElementById("botonAnadirLinea").addEventListener("click", anadirLinea);
document.getElementById("botonEnviarPedido").addEventListener("click", enviarPedido);
document.getElementById("botonConsultarPedidos").addEventListener("click", consultarPedidos);

mostrarCamposDelTipo();
cargarTodo();
