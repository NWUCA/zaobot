from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP

from .task import send_60s

daily60s = on_command('60s', aliases={'60', }, permission=GROUP, priority=5, block=True)
@daily60s.handle()
async def _(event: GroupMessageEvent):
    await send_60s(event.group_id)
