from typing import Union
from datetime import datetime, date

import nonebot
import httpx


q_weather_key = nonebot.get_driver().config.q_weather_key
format_url = 'https://devapi.qweather.com/v7/grid-weather/3d?location={},{}&key={}'

async def request_grid_weather_3d(e: float, n: float) -> dict:
    url = format_url.format(e, n, q_weather_key)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        raise ValueError
    return response.json()

async def get_grid_weather_today(e: float, n: float) -> Union[dict, None]:
    data = await request_grid_weather_3d(e, n)
    for today in data['daily']:
        if today['fxDate'] == date.today().isoformat():
            break
    else:
        return None
    return {
        'update_time': datetime.fromisoformat(data['updateTime']), # 更新时间
        'date':        date_week_str(date.fromisoformat(today['fxDate'])), # 预报日期
        'temp_max':    today['tempMax'],
        'temp_min':    today['tempMin'],
        'text_day':    today['textDay'],
        'text_night':  today['textNight'],
        'precip':      int(float(today['precip'])), # 降水量
        'humidity':    today['humidity'], # 相对湿度
    }

def date_week_str(d: date) -> str:
    return d.strftime('%Y年%m月%d日') + ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][d.weekday()]
