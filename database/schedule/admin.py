from sqladmin.models import ModelView
from database import register
from .model import Task, CronTrigger, GroupCronTriggerTask

@register
class TaskAdmin(ModelView, model=Task):
    form_include_pk = True
    can_create = False
    can_delete = False
    column_list = [
        Task.key,
        Task.usable,
    ]


@register
class CronTriggerAdmin(ModelView, model=CronTrigger):
    form_include_pk = False
    column_list = [
        CronTrigger.brief,
    ]

@register
class GroupCronTriggerTaskAdmin(ModelView, model=GroupCronTriggerTask):
    form_include_pk = False
    column_list = [
        GroupCronTriggerTask.group,
        GroupCronTriggerTask.task,
        GroupCronTriggerTask.cron_trigger,
    ]
