import string
from random import sample
from pathlib import Path
from importlib import import_module
from typing import Callable

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base

from sqladmin.application import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

class Register:
    def __init__(self) -> None:
        self.members = []
    def __call__(self, cls) -> None:
        self.members.append(cls)

register = Register()


Base = declarative_base()

for path in Path(__package__).iterdir():
    if path.is_file():
        continue
    if (path / 'model.py').is_file():
        module_name = f'.{path.name}.model'
        import_module(module_name, __package__)
    if (path / 'admin.py').is_file():
        module_name = f'.{path.name}.admin'
        import_module(module_name, __package__)

class AsyncDatabase:
    engine:  AsyncEngine                = None
    session: Callable[[], AsyncSession] = None

admin: Admin = None

def connect(
    database_url: str,
    secret: str,
    username: str,
    password: str,
    app
):
    global admin
    AsyncDatabase.engine = create_async_engine(database_url, echo=True)
    AsyncDatabase.session = sessionmaker(AsyncDatabase.engine, expire_on_commit=False, class_=AsyncSession)

    authentication_backend = MyBackend(secret, username, password)
    admin = Admin(app, AsyncDatabase.engine, authentication_backend=authentication_backend)

    for view in register.members:
        admin.add_view(view)

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


