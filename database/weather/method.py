from typing import Union

from datetime import datetime, date, timedelta
from typing import Union

from sqlalchemy.sql.expression import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncResult
from database import AsyncDatabase as AD

from .model import GroupGridWeather3d

async def get_last_group_grid_weather_3d(group_id: str) -> Union[GroupGridWeather3d, None]:
    async with AD.session() as session:
        async with session.begin():
            result: AsyncResult = await session.execute(
                select(GroupGridWeather3d)
                .where(and_(
                    GroupGridWeather3d.group_id      == group_id,
                    GroupGridWeather3d.forecast_date == date.today(),
                    GroupGridWeather3d.update_time   >= datetime.now() - timedelta(hours=1),
                ))
                .order_by(desc(GroupGridWeather3d.request_time))
            )
    return result.first()

async def store_group_grid_weather_3d(
    group_id: str,
    raw_json: str,
    update_time: datetime,
    forecast_date: date,
):
    async with AD.session() as session:
        async with session.begin():
            session.add(GroupGridWeather3d(
                group_id=group_id,
                raw_json=raw_json,
                update_time=update_time,
                forecast_date=forecast_date
            ))
