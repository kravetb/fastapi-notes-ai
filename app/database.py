from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.SQLALCHEMY_DB_URL, echo=True)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    print(settings.SQLALCHEMY_DB_URL)
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
