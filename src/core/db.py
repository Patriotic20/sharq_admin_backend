from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

engine = create_async_engine(settings.connection_string, echo=False)


AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)


async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


Base = declarative_base()
