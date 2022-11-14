from sqladmin.models import ModelView
from database import register
from .model import Group, GroupLocation, GroupMessage, GroupNotice

@register
class GroupAdmin(ModelView, model=Group):
    form_include_pk = True
    column_list = [
        Group.id,
        Group.name,
    ]
    form_widget_args = dict(location=dict(readonly=True))

@register
class GroupLocationAdmin(ModelView, model=GroupLocation):
    column_list = [
        GroupLocation.group_id,
        GroupLocation.brief,
        GroupLocation.province,
        GroupLocation.city,
        GroupLocation.district,
    ]

@register
class GroupMessageAdmin(ModelView, model=GroupMessage):
    column_list = [
        GroupMessage.message_id,
        GroupMessage.qq_id,
        GroupMessage.group_id,
        GroupMessage.message,
        GroupMessage.datetime,
    ]
    column_sortable_list = [GroupMessage.datetime]

@register
class GroupNoticeAdmin(ModelView, model=GroupNotice):
    column_list = [
        GroupNotice.id,
        GroupNotice.group_id,
        GroupNotice.title,
        GroupNotice.date,
        GroupNotice.fixed,
    ]
