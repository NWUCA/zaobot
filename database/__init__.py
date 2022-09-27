from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AsyncDatabase:
    engine:  AsyncEngine  = None
    session: AsyncSession = None

def connect(database_url):
    AsyncDatabase.engine = create_async_engine(database_url, echo=True)
    AsyncDatabase.session = sessionmaker(AsyncDatabase.engine, expire_on_commit=False, class_=AsyncSession)

async def disconnect():
    await AsyncDatabase.engine.dispose()

from .record import GroupMessage
from .zao import ZaoBoy
