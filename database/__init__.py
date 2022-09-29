from typing import Callable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqladmin import Admin
from fastapi import FastAPI

Base = declarative_base()

from .record import GroupMessage, GroupMessageAdmin
from .zao import ZaoGuy, ZaoGuyAdmin

class AsyncDatabase:
    engine:  AsyncEngine                = None
    session: Callable[[], AsyncSession] = None
    admin:   Admin                      = None

def connect(database_url, app):
    AsyncDatabase.engine = create_async_engine(database_url, echo=True)
    AsyncDatabase.session = sessionmaker(AsyncDatabase.engine, expire_on_commit=False, class_=AsyncSession)

    AsyncDatabase.admin = Admin(app, AsyncDatabase.engine)
    AsyncDatabase.admin.add_view(GroupMessageAdmin)
    AsyncDatabase.admin.add_view(ZaoGuyAdmin)

async def disconnect():
    await AsyncDatabase.engine.dispose()
