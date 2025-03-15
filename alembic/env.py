import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from app.database import Base
from app.models import models
from app.config import get_settings

settings = get_settings()

# Налаштування логування
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Вкажіть вашу метадані
target_metadata = Base.metadata

# Оновлюємо URL бази даних із змінного середовища
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DB_URL)

# Створення асинхронного двигуна
def get_engine():
    return create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

async def run_migrations_online():
    """Асинхронний режим міграцій."""
    engine = get_engine()
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Синхронна функція для запуску міграцій."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        render_as_batch=True  # Особливо важливо для SQLite
    )

    with context.begin_transaction():
        context.run_migrations()

# Визначаємо, як запускати міграції
if context.is_offline_mode():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        render_as_batch=True  # Особливо важливо для SQLite
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())
