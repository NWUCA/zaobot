from io import StringIO

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import httpx

sxcx = on_command('sxcx')
@sxcx.handle()
async def _(bot: Bot, event: Event, state: T_State):
    sx = str(event.get_message()).strip()
    if sx:
        state['sx'] = sx

@sxcx.got('sx', prompt='你要查询什么呢')
async def _(bot: Bot, event: Event, state: T_State):
    data = {'text': state['sx']}
    async with httpx.AsyncClient() as client:
        response = await client.post('https://lab.magiconch.com/api/nbnhhsh/guess', json=data)
    if response.status_code != 200:
        await sxcx.finish('上游似乎出锅了QAQ，或者你输入了奇怪的东西WWW')
    msg = ''
    for tran in response.json():
        if not tran.__contains__('trans'):
            continue
        with StringIO() as buffer:
            print(*tran['trans'], sep=', ', file=buffer)
            buffer.seek(0)
            msg += f'{tran["name"]}: {buffer.read()}'
    await sxcx.finish(msg[:-1])
