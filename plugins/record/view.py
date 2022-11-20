from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from database.group.method import store_group_msg

store = on_message(block=False, permission=GROUP, priority=1)
@store.handle()
async def _(event: GroupMessageEvent):
    if msg := event.raw_message:
        await store_group_msg(event.user_id, event.group_id, event.message_id, msg)
