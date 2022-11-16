from sqladmin.models import ModelView
from database.admin import admin_register
from .model import Task, CronGroupTask

@admin_register
class TaskAdmin(ModelView, model=Task):
    form_include_pk = True
    can_create = False
    can_delete = False
    column_list = [
        Task.key,
        Task.usable,
    ]

@admin_register
class CronGroupTaskAdmin(ModelView, model=CronGroupTask):
    form_include_pk = False
    column_list = [
        CronGroupTask.group,
        CronGroupTask.task,
        CronGroupTask.brief,
    ]
