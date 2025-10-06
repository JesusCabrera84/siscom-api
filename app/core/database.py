from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Motor con configuración de pool
engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,
    pool_size=settings.DB_MIN_CONNECTIONS,
    max_overflow=settings.DB_MAX_CONNECTIONS - settings.DB_MIN_CONNECTIONS,
    pool_timeout=settings.DB_CONNECTION_TIMEOUT_SECS,
    pool_recycle=settings.DB_IDLE_TIMEOUT_SECS,
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session
