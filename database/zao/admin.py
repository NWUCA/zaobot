from sqladmin.models import ModelView
from database import register
from .model import ZaoGuy

@register
class ZaoGuyAdmin(ModelView, model=ZaoGuy):
    column_list = [
        ZaoGuy.id,
        ZaoGuy.qq_id,
        ZaoGuy.group_id,
        ZaoGuy.nickname,
        ZaoGuy.zao_datetime,
        ZaoGuy.wan_datetime,
    ]
