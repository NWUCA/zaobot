from sqlalchemy import event
from sqlalchemy.orm import Mapper
from sqlalchemy.engine import Connection

from nonebot_plugin_apscheduler import scheduler

from database import on_connected
from database.schedule.model import CronGroupTask
from database.schedule.decorator import task_register

from .method import get_all_cron_group_tasks

def add_cron_group_task(task: CronGroupTask):
    scheduler.add_job(
        task_register.get(task.task_key),
        'cron',
        id=str(task.id),
        kwargs={'group_id': task.group_id},
        **task.param,
    )
    print('添加定时任务', task.brief)

def remove_cron_group_task(target: CronGroupTask):
    scheduler.remove_job(str(target.id))

@event.listens_for(CronGroupTask, 'after_insert')
def receive_after_update(mapper: Mapper, connection: Connection, target: CronGroupTask):
    add_cron_group_task(target)

@event.listens_for(CronGroupTask, 'after_delete')
def receive_after_update(mapper: Mapper, connection: Connection, target: CronGroupTask):
    remove_cron_group_task(target)

@event.listens_for(CronGroupTask, 'after_update')
def receive_after_update(mapper: Mapper, connection: Connection, target: CronGroupTask):
    remove_cron_group_task(target)
    add_cron_group_task(target)

@on_connected
def add_all_cron_group_tasks():
    tasks = get_all_cron_group_tasks()
    for task in tasks:
        add_cron_group_task(task)
