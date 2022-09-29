from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import httpx

ask = on_command('ask')
@ask.handle()
async def _(bot: Bot, event: Event, state: T_State):
    question = str(event.get_message()).strip()
    if question:
        state['question'] = question

@ask.got('question', prompt='说一个二元问题(´・ω・`)')
async def _(bot: Bot, event: Event, state: T_State):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://yesno.wtf/api/', timeout=60)
    ans = response.json()
    await ask.finish([
        {"type": "reply", "data": {"id": event.message_id}},
        {"type": "text", "data": {"text": ans['answer'].upper() + '\x0a'}},
        {"type": "image", "data": {"file": ans['image']}},
    ])
