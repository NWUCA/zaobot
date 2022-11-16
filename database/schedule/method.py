from .decorator import register
from io import StringIO
from datetime import timedelta, datetime, date
from typing import Any, Callable, List
from sqlalchemy.sql.expression import update
from sqlalchemy.ext.asyncio import AsyncResult
from database import AsyncDatabase as AD
from .model import Task

async def update_tasks():
    async with AD.session() as session:
        async with session.begin():
            session.execute(update(Task).values(usable=False))
            for key in register.members:
                await session.merge(Task(key=key, usable=True))

