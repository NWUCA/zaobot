import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment

from database.schedule.decorator import task_register
from database.group.method import get_group_location

from .data_source import get_grid_weather_today, gen_weather_card_image

@task_register(key='推送今日网格天气')
async def _(group_id: str):
    await send_image_weather_card(group_id)

async def send_image_weather_card(group_id: str):
    location = await get_group_location(group_id)
    if location is None or location.east_longitude is None or location.north_latitude is None:
        print('请在后台设置经纬度坐标')
        return
    img = await gen_weather_card_image(location.east_longitude, location.north_latitude, location.brief)
    if not img:
        print('生成天气卡片失败')
        return
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=MessageSegment.image(img))


async def send_message_grid_weather_today(group_id: str):
    # 弃用
    location = await get_group_location(group_id)
    if location is None or location.east_longitude is None or location.north_latitude is None:
        print('请在后台设置经纬度坐标')
        return

    data = await get_grid_weather_today(location.east_longitude, location.north_latitude)
    if data is None:
        print('获取失败')
        return
    
    msg = (
        f"今天是{data['date']}\x0a"
        f"以下是{location.brief}天气预报\x0a"
        f"白天【{data['text_day']}】, 夜间【{data['text_night']}】\x0a"
        f"最低/高气温 {data['temp_min']}/{data['temp_max']}℃\x0a"
        f"相对湿度 {data['humidity']}%\x0a"
    )
    if data['precip'] != 0:
        msg += f"降水量 {data['precip']}mm\x0a"
    msg += f"数据更新时间 {data['update_time'].strftime('%H:%M')}"

    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=msg)
