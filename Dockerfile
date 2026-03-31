# Usamos 3.12-slim por estabilidad con las librerías de audio
FROM python:3.12-slim

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 1. Instalar dependencias del sistema necesarias para compilar y procesar audio
# webrtcvad requiere gcc (build-essential) y python3-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libsndfile1 \
    ffmpeg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiar solo los archivos de dependencias para aprovechar el caché de Docker
COPY pyproject.toml uv.lock ./

# 3. Instalar las dependencias de Python (aquí se compilará webrtcvad)
# Esto se guardará en caché y no se repetirá a menos que cambies el pyproject.toml
RUN uv sync --frozen --no-dev

# 4. Copiar el resto del código de la aplicación
COPY . .

# 5. Colocar el entorno virtual en el PATH
ENV PATH="/app/.venv/bin:$PATH"

# 6. Ejecutar la aplicación apuntando correctamente a src/main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]