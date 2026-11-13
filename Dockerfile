# Imagen de la API de la Tienda Online (FastAPI + Uvicorn)
FROM python:3.12-slim

# - PYTHONDONTWRITEBYTECODE / PYTHONUNBUFFERED: sin .pyc y con logs en tiempo real
# - UVICORN_HOST / UVICORN_PORT: uvicorn los lee como variables de entorno,
#   así host y puerto se pueden cambiar con `docker run -e ...` sin tocar el código
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

WORKDIR /app

# 1) Primero solo las dependencias: esta capa se reutiliza de la caché mientras no cambie requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2) Usuario sin privilegios: la aplicación no se ejecuta como root
RUN useradd --create-home --uid 10001 appuser

# 3) Código fuente de la API; --chown da permisos al usuario appuser sobre el código
COPY --chown=appuser:appuser src/Tienda_online/ .

USER appuser

EXPOSE 8000

# Comprueba que la API responde (la documentación /docs siempre está disponible)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ['UVICORN_PORT'] + '/docs', timeout=3)"

# Host y puerto salen de UVICORN_HOST y UVICORN_PORT
CMD ["uvicorn", "main:app"]
