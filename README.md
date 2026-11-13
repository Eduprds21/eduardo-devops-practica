# Tienda Online – DevOps práctica

- **Proyecto:** Tienda Online (API REST + cliente Python + frontend web)
- **Autor:** Eduardo Paredes Agrelo
- **Repositorio:** https://github.com/Eduprds21/Arquitectura-del-Software
- **Asignatura:** Arquitectura del Software – Universidad Intercontinental de la Empresa (UIE)

## Descripción

Aplicación Python que gestiona una tienda online mediante una API REST construida con **FastAPI**.
Permite crear y consultar usuarios (clientes y administradores), gestionar un inventario de productos
(genéricos, electrónicos y de ropa) y registrar pedidos con control de stock.

Es el resultado de la Práctica 2 (API REST, cliente Python y frontend) y se gestiona con Git/GitHub
(Práctica 3.1) y se contenedoriza con Docker (Práctica 3.2). Los datos viven en memoria: al reiniciar
la API (o el contenedor) se pierden.

## Estructura del repositorio

```text
.
├── src/
│   ├── Tienda_online/      API FastAPI (main.py, schemas.py, models/, Services/)
│   ├── Cliente_python/     Cliente con la librería requests (cliente_tienda.py)
│   └── Frontend/           Página web (index.html, app.js, estilos.css)
├── Dockerfile              Imagen de la API (python:3.12-slim)
├── .dockerignore           Ficheros excluidos del contexto de build
├── requirements.txt        Dependencias con versiones fijadas
└── README.md
```

## Ejecución local (sin Docker)

Requiere Python 3.12.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cd src/Tienda_online
uvicorn main:app --reload
```

Documentación interactiva: <http://localhost:8000/docs>

## Docker

### 1. Construir la imagen

Desde la raíz del repositorio:

```bash
docker build -t tienda-online-api:1.0 -t tienda-online-api:latest .
```

La imagen parte de `python:3.12-slim`, instala `requirements.txt` en una capa propia (se reutiliza de la
caché mientras no cambien las dependencias), copia solo `src/Tienda_online/` y ejecuta la API con un usuario
sin privilegios (`appuser`). El `.dockerignore` deja fuera `.git`, cachés, entornos virtuales, `tests/`, etc.

### 2. Ejecutar el contenedor

```bash
# En primer plano, publicando el puerto 8000
docker run --rm -p 8000:8000 --name tienda-api tienda-online-api:1.0
```

```bash
# En segundo plano
docker run -d -p 8000:8000 --name tienda-api tienda-online-api:1.0
docker logs -f tienda-api      # ver los logs
docker stop tienda-api         # parar (y borrar con --rm / docker rm tienda-api)
```

```bash
# Con otro puerto en el equipo (8080) y otro puerto dentro del contenedor (9000)
docker run --rm -e UVICORN_PORT=9000 -p 8080:9000 tienda-online-api:1.0
```

Una vez arrancada, la API está en <http://localhost:8000> y se puede usar desde otros equipos de la red con
`http://IP_DEL_EQUIPO:8000`.

### 3. Variables de entorno soportadas

La aplicación no necesita secretos ni claves. Se puede configurar el servidor con las variables de
[Uvicorn](https://www.uvicorn.org/settings/), que ya vienen definidas en la imagen:

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `UVICORN_HOST` | `0.0.0.0` | Interfaz en la que escucha dentro del contenedor (debe ser `0.0.0.0` para poder publicar el puerto). |
| `UVICORN_PORT` | `8000` | Puerto dentro del contenedor (cambiar también el `-p` de `docker run`). |

Si en el futuro hubiese secretos, se pasarían con `-e CLAVE=valor` o `--env-file .env` (el `.env` está en
`.gitignore` y `.dockerignore`, nunca se sube al repositorio).

### 4. Probar que funciona

Con el contenedor arrancado:

1. **Documentación interactiva:** abrir <http://localhost:8000/docs> y comprobar que aparecen los endpoints.
2. **Estado del contenedor:** `docker ps` debe mostrar `healthy` (la imagen define un `HEALTHCHECK` sobre `/docs`).
3. **Logs esperados** (`docker logs tienda-api`):

   ```text
   INFO:     Started server process [1]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

4. **Endpoints de ejemplo:**

   ```bash
   curl http://localhost:8000/productos                      # -> [] (200)
   curl -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
        -d '{"tipo":"generico","nombre":"Botella reutilizable","precio":9.5,"stock":50}'   # -> 201
   curl http://localhost:8000/usuarios/noexiste              # -> 404 {"detail": "No existe el usuario 'noexiste'."}
   ```

5. **Cliente Python** (en otra terminal, con `pip install -r requirements.txt` hecho):

   ```bash
   cd src/Cliente_python
   python cliente_tienda.py http://localhost:8000
   ```

   Debe imprimir `[OK] POST /usuarios -> 201`, `[OK] GET /usuarios -> 200`, … hasta terminar con
   `[OK] POST /pedidos -> 409` y `[OK] GET /usuarios/noexiste -> 404` (errores esperados a propósito).

6. **Frontend:** abrir `src/Frontend/index.html` en el navegador; el campo **Servidor** ya apunta a
   `http://localhost:8000`.

### 5. Descargar la imagen publicada (pull)

La imagen está publicada en un registry; no hace falta clonar el repositorio para usarla:

```bash
docker pull ghcr.io/eduprds21/tienda-online-api:1.0
docker run --rm -p 8000:8000 ghcr.io/eduprds21/tienda-online-api:1.0
```

### 6. Publicar la imagen (build → run → test → push)

```bash
docker build -t tienda-online-api:1.0 .
docker run -d -p 8000:8000 --name tienda-api tienda-online-api:1.0      # run
python src/Cliente_python/cliente_tienda.py http://localhost:8000       # test
docker stop tienda-api
docker tag tienda-online-api:1.0 ghcr.io/eduprds21/tienda-online-api:1.0
docker login ghcr.io -u Eduprds21
docker push ghcr.io/eduprds21/tienda-online-api:1.0                      # push
```

## Flujo de trabajo con Git

- `main` es la rama estable: solo recibe cambios mediante Pull Request.
- Una rama corta por tarea (`feature/docker`, …), con commits pequeños y descriptivos
  (`feat(docker): …`, `docs: …`, `chore: …`).
- No se suben secretos (`.env` ignorado); `.gitignore` y `.dockerignore` evitan ficheros innecesarios.
