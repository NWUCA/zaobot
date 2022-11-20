from sqladmin.models import ModelView
from database.admin import admin_register
from .model import GroupGridWeather3d

@admin_register
class GroupGridWeather3dAdmin(ModelView, model=GroupGridWeather3d):
    column_list = [
        GroupGridWeather3d.group_id,
        GroupGridWeather3d.request_time,
        GroupGridWeather3d.update_time,
        GroupGridWeather3d.forecast_date,
    ]
    column_sortable_list = [GroupGridWeather3d.request_time]

