import string
from random import sample

from sqladmin.application import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from .util import load_subdirs_module

class AdminRegister:
    def __init__(self) -> None:
        self.members = []
    def __call__(self, cls) -> None:
        self.members.append(cls)

admin_register = AdminRegister()

load_subdirs_module('admin')

admin: Admin = None

def start_admin(
    secret: str,
    username: str,
    password: str,
    app
):
    global admin
    from . import Database
    authentication_backend = MyBackend(secret, username, password)
    admin = Admin(app, Database.async_engine, authentication_backend=authentication_backend)

    for view in admin_register.members:
        admin.add_view(view)


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


