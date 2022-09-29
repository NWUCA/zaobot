from nonebot.plugin import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from .data_source import should_fudu

fudu = on_message(priority=100)
@fudu.handle()
async def _(event: GroupMessageEvent):
    if should_fudu(event.group_id, event.raw_message):
        await fudu.finish(event.raw_message)
