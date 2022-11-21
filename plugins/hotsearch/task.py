from datetime import datetime
import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from database.schedule.decorator import task_register
from .data_source import get_weibo_hot_search, gen_weibo_hot_search_image

@task_register(key='推送实时微博热搜榜')
async def _(group_id: str):
    await send_message_weibo_hot_search(group_id)

async def send_message_weibo_hot_search(group_id: str):

    data = await get_weibo_hot_search()
    if not data:
        print('获取微博热搜榜失败')
        return
    msg = datetime.now().strftime('微博热搜榜 %m月%d日 %H:%M:')
    msg += f"\x0agov. {data['hotgov']['word'].strip('#')}"
    for index, rs in enumerate(data['realtime'][:10], 1):
        msg += f"\x0a{index}. {rs['word']}"
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=msg)

@task_register(key='推送实时微博热搜榜图片')
async def _(group_id: str):
    await send_image_weibo_hot_search(group_id)

async def send_image_weibo_hot_search(group_id: str):
    img = await gen_weibo_hot_search_image()
    if not img:
        print('获取微博热搜榜失败')
        return
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=QQMS.image(img))
