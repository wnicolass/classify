import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession
)
from sqlalchemy.ext.declarative import declarative_base

load_dotenv(find_dotenv())

engine: AsyncEngine = create_async_engine(url = os.getenv('CONNECTION_STRING'))
Session: AsyncSession = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine,
    _class = AsyncSession
)
Base = declarative_base()

async def create_metadata() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

