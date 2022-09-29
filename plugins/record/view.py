from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from .data_source import store_msg

store = on_message(block=False, permission=GROUP, priority=1)
@store.handle()
async def _(event: GroupMessageEvent):
    uid = event.user_id
    gid = event.group_id
    msg = event.raw_message
    if msg:
        await store_msg(uid, gid, msg)
