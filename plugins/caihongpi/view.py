from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import httpx

chp = on_command('chp')
@chp.handle()
async def _(bot: Bot, event: Event, state: T_State):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://chp.shadiao.app/api.php')
    if response.status_code == 200:
        await chp.finish(response.text)
