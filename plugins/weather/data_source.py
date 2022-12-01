import pytz
import aiofiles
from pathlib import Path
from typing import Union, Dict, Tuple
from datetime import datetime, date

import nonebot
import httpx
from jinja2 import Environment, FileSystemLoader

from plugins.playwright import get_new_page, get_playwright

q_weather_key = nonebot.get_driver().config.q_weather_key

format_url_weather_now = 'https://devapi.qweather.com/v7/grid-weather/now?location={},{}&key={}'
format_url_weather_24h = 'https://devapi.qweather.com/v7/grid-weather/24h?location={},{}&key={}'
format_url_weather_3d  = 'https://devapi.qweather.com/v7/weather/3d?location={},{}&key={}'
format_url_indices     = 'https://devapi.qweather.com/v7/indices/1d?location={},{}&key={}&type=0'
format_url_warning     = 'https://devapi.qweather.com/v7/warning/now?location={},{}&key={}'
format_url_air         = 'https://devapi.qweather.com/v7/air/now?location={},{}&key={}'

async def request_grid_weather_3d(e: float, n: float) -> dict:
    # 弃用
    url = format_url_weather_3d.format(e, n, q_weather_key)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        raise ValueError
    return response.json()

async def get_grid_weather_today(e: float, n: float) -> Union[dict, None]:
    # 弃用
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

async def gen_weather_card_image(e: float, n: float, location: str) -> bytes:
    weather_now, weather_24h, weather_3d, indices, warning, air = await get_weather_data(e, n)

    now_datetime = datetime.now().replace(tzinfo=pytz.UTC)
    now_date = now_datetime.date()
    time_string = date_week_time_str(now_datetime)

    for today in weather_3d['daily']:
        if today['fxDate'] == now_date.isoformat():
            break
    else:
        return None

    for index in indices['daily']:
        if index['type'] == '8':
            comfortable_text = index['text']
            break
    else:
        comfortable_text = '美好的一天。'


    max_temp = max(map(float, [h['temp'] for h in weather_24h['hourly']]))
    min_temp = min(map(float, [h['temp'] for h in weather_24h['hourly']]))
    if min_temp >= max_temp:
        min_temp = max_temp - 1

    now_index = 0
    future_24h = list()
    for hourly in weather_24h['hourly'][::2]:
        temp = float(hourly['temp'])
        height = (temp - min_temp) / (max_temp - min_temp) * 10 + 2
        fx_time = datetime.fromisoformat(hourly['fxTime'])
        future_24h.append({
            'time': fx_time.strftime('%I%p'),
            'temp': hourly['temp'],
            'icon': hourly['icon'],
            'height': int(height),
        })
        if fx_time <= now_datetime :
            now_index += 1

    air = air['now']
    aqi = {
        'aqi': int(float(air['aqi'])),
        'category': air['category'],
        'detail': [
            {'name': 'PM2.5', 'value': air['pm2p5'], 'percent': percent_from_avg(air['pm2p5'], 10)},
            {'name': 'PM10',  'value': air['pm10'],  'percent': percent_from_avg(air['pm10'],  20)},
            {'name': 'NO₂',   'value': air['no2'],   'percent': percent_from_avg(air['no2'],   40)},
            {'name': 'SO₂',   'value': air['so2'],   'percent': percent_from_avg(air['so2'],   20)},
            {'name': 'CO',    'value': air['co'],    'percent': percent_from_avg(air['co'],    4)},
            {'name': 'O₃',    'value': air['o3'],    'percent': percent_from_avg(air['o3'],    100)},
        ]
    }

    async with aiofiles.open(Path(__file__).parent / 'template/weather_card.jinja2', 'r') as f:
        jinja2_template = await f.read()

    loader = FileSystemLoader(Path(__file__).parent)
    environment = Environment(loader=loader, enable_async=True)
    template = environment.from_string(jinja2_template)
    html = await template.render_async(
        time_string=time_string,
        address_string=location,
        comfortable_text=comfortable_text,
        now=weather_now['now'],
        today=today,
        future_24h=future_24h,
        aqi=aqi,
        warning=warning['warning'],
        now_index=now_index,
    )

    async with get_new_page(**get_playwright().devices['iPhone 12']) as page:
        await page.add_style_tag(url='https://cdn.jsdelivr.net/npm/qweather-icons@1.1.1/font/qweather-icons.css')
        await page.set_content(html)
        return await page.screenshot(timeout=60_000, full_page=True)


def percent_from_avg(val: float, avg: float):
    return min(float(val) / avg / 8, 1)


def date_week_str(d: date) -> str:
    return d.strftime('%Y年%m月%d日') + ' ' + ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][d.weekday()]

def date_week_time_str(d: datetime) -> str:
    return date_week_str(d.date()) + ' ' + d.strftime('%H:%M')

async def get_json_data(client, format_url, *data):
    res = await client.get(format_url.format(*data))
    return res.json()

async def get_weather_data(e: float, n: float) -> Tuple[Dict, Dict, Dict, Dict, Dict, Dict]:
    async with httpx.AsyncClient() as client:
        weather_now = await get_json_data(client, format_url_weather_now, e, n, q_weather_key)
        weather_24h = await get_json_data(client, format_url_weather_24h, e, n, q_weather_key)
        weather_3d  = await get_json_data(client, format_url_weather_3d,  e, n, q_weather_key)
        indices     = await get_json_data(client, format_url_indices,     e, n, q_weather_key)
        warning     = await get_json_data(client, format_url_warning,     e, n, q_weather_key)
        air         = await get_json_data(client, format_url_air,         e, n, q_weather_key)
    return weather_now, weather_24h, weather_3d, indices, warning, air
