# Etapa de construcción
FROM python:3.12-slim AS builder

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para resemblyzer y psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias sin instalar el proyecto (cache layer)
RUN uv sync --frozen --no-install-project --no-dev

# Copiar el código de la aplicación
COPY . .

# Instalar el proyecto
RUN uv sync --frozen --no-dev

# Etapa final para ejecución
FROM python:3.12-slim

WORKDIR /app

# Copiar dependencias del sistema necesarias para ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual y el código desde el builder
COPY --from=builder /app /app

# Asegurarse de usar el entorno virtual creado por uv
ENV PATH="/app/.venv/bin:$PATH"

# Comando para iniciar la aplicación con Gunicorn y Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000"]