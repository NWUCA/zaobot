from sqladmin.models import ModelView
from database.admin import admin_register
from .model import ZaoGuy

@admin_register
class ZaoGuyAdmin(ModelView, model=ZaoGuy):
    column_list = [
        ZaoGuy.id,
        ZaoGuy.qq_id,
        ZaoGuy.group_id,
        ZaoGuy.nickname,
        ZaoGuy.zao_datetime,
        ZaoGuy.wan_datetime,
    ]
