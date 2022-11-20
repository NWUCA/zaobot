from typing import List
from sqlalchemy.sql.expression import update

from database import Database
from .decorator import task_register
from .model import Task, CronGroupTask

async def update_tasks():
    async with Database.async_session() as session:
        async with session.begin():
            await session.execute(update(Task).values(usable=False))
            for key in task_register.members:
                await session.merge(Task(key=key, usable=True))

def get_all_cron_group_tasks() -> List[CronGroupTask]:
    return Database.sync_session().query(CronGroupTask).all()
