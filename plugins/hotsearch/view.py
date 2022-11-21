from datetime import date

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.params import CommandArg

from .task import send_image_weibo_hot_search

weibo_hot_search = on_command('rs', aliases={'resou', 'wbrs', '热搜', '微博热搜'}, permission=GROUP, priority=5, block=True)
@weibo_hot_search.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    # await send_message_weibo_hot_search(event.group_id)
    await send_image_weibo_hot_search(event.group_id)

