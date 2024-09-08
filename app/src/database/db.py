from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import redis.asyncio as redis_async
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
# SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url.replace("postgresql://", "postgresql+asyncpg://")

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine, class_=AsyncSession)

redis_client_async = redis_async.Redis(host=settings.redis_host, 
                        port=settings.redis_port, 
                        db=0 
                        )

# Dependency
# def get_db():
#
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
