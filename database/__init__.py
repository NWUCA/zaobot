from random import sample
import string
from typing import Callable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .record import GroupMessage, GroupMessageAdmin
from .zao import ZaoGuy, ZaoGuyAdmin
from .notice import Notice, NoticeAdmin
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

class AsyncDatabase:
    engine:  AsyncEngine                = None
    session: Callable[[], AsyncSession] = None
    admin:   Admin                      = None

def connect(
    database_url: str,
    secret: str,
    username: str,
    password: str,
    app
):
    AsyncDatabase.engine = create_async_engine(database_url, echo=True)
    AsyncDatabase.session = sessionmaker(AsyncDatabase.engine, expire_on_commit=False, class_=AsyncSession)

    authentication_backend = MyBackend(secret, username, password)
    AsyncDatabase.admin = Admin(app, AsyncDatabase.engine, authentication_backend=authentication_backend)
    AsyncDatabase.admin.add_view(GroupMessageAdmin)
    AsyncDatabase.admin.add_view(ZaoGuyAdmin)
    AsyncDatabase.admin.add_view(NoticeAdmin)

async def disconnect():
    await AsyncDatabase.engine.dispose()

class MyBackend(AuthenticationBackend):

    def __init__(self, secret_key: str, username: str, password: str) -> None:
        super().__init__(secret_key)
        self.username = username
        self.password = password
        self.token = ''.join(sample(string.ascii_letters, 32))

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        if username == self.username and password == self.password:
            self.token = ''.join(sample(string.ascii_letters, 32))
            request.session.update({"token": self.token})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        if token == self.token:
            return True

        return False
