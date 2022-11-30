from datetime import date

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.params import CommandArg

from .task import send_image_weather_card

grid_weather_today = on_command('weather', aliases={'tq', '天气', '今日天气'}, permission=GROUP, priority=5, block=True)
@grid_weather_today.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    await send_image_weather_card(event.group_id)
