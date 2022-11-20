from io import StringIO

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.params import CommandArg

import httpx

sxcx = on_command('sxcx', aliases={'缩写查询', 'suoxie'}, permission=GROUP, priority=5, block=True)
@sxcx.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    text = arg.extract_plain_text().strip()
    if reply := event.reply:
        text += reply.message.extract_plain_text().strip()
    if not text:
        return
    async with httpx.AsyncClient() as client:
        response = await client.post('https://lab.magiconch.com/api/nbnhhsh/guess', json={'text': text})
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
