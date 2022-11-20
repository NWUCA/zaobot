from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.params import CommandArg
import httpx

ask = on_command('ask', permission=GROUP, priority=5, block=True)
@ask.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    question = arg.extract_plain_text().strip()
    if not question:
        return
    async with httpx.AsyncClient() as client:
        response = await client.get('https://yesno.wtf/api/', timeout=60)
    ans = response.json()
    await ask.finish([
        MessageSegment(type='reply', data={"id":   event.message_id}),
        MessageSegment(type='text',  data={"text": ans['answer'].upper() + '\x0a'}),
        MessageSegment(type='image', data={"file": ans['image']}),
    ])
