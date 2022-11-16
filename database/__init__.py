from typing import Callable

from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base

from .util import load_subdirs_module

Base = declarative_base()

load_subdirs_module('model')

class OnConnected:
    def __init__(self) -> None:
        self.members = []
    def __call__(self, func: Callable) -> None:
        self.members.append(func)

on_connected = OnConnected()

class Database:
    sync_engine:   Engine                     = None
    sync_session:  Callable[[], Session]      = None
    async_engine:  AsyncEngine                = None
    async_session: Callable[[], AsyncSession] = None

    @staticmethod
    def connect(
        sync_database_url:  str,
        async_database_url: str,
    ):
        Database.async_engine  = create_async_engine(async_database_url, echo=True)
        Database.async_session = sessionmaker(Database.async_engine, expire_on_commit=False, class_=AsyncSession)
        Database.sync_engine   = create_engine(sync_database_url, echo=True)
        Database.sync_session  = sessionmaker(Database.sync_engine, expire_on_commit=False, class_=Session)

        load_subdirs_module('listen')

        for func in on_connected.members:
            func()

    @staticmethod
    async def disconnect():
        await Database.async_engine.dispose()


