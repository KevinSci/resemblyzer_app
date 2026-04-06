FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync --frozen --no-cache
CMD ["uv", "run", "fastapi", "run", "src/main.py", "--port", "5000"]
