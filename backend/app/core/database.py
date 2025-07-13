"""Configuration de la base de données SQLAlchemy."""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import Generator, AsyncGenerator
import asyncio
import asyncpg

from app.core.config import settings

# Configuration synchrone
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration asynchrone
async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Metadata et base déclarative
metadata = MetaData()
Base = declarative_base(metadata=metadata)


def get_db() -> Generator[SessionLocal, None, None]:
    """Obtenir une session de base de données synchrone."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtenir une session de base de données asynchrone."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialiser la base de données."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Base de données initialisée avec succès")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise


async def close_db_connections() -> None:
    """Fermer les connexions à la base de données."""
    await async_engine.dispose()
    engine.dispose()


# Test de connexion
async def test_db_connection() -> bool:
    """Tester la connexion à la base de données."""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return False