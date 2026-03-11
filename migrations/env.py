import os
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from dotenv import load_dotenv
from alembic import context

# Importa tus modelos para que Base.metadata los reconozca
from src.models import Base 

# 1. Cargar variables de entorno con validación
load_dotenv()
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL no encontrada en el entorno. Verifica tu archivo .env")

config = context.config

# 2. Sincronizar la URL con el objeto config de Alembic
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # En lugar de engine_from_config, usamos create_engine directamente
    # para mayor claridad dado que ya manejamos la URL.
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()