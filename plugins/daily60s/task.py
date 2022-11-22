import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from database.schedule.decorator import task_register
from .data_source import get_60s_image

@task_register(key='推送每日60秒读懂世界')
async def _(group_id: str):
    await send_60s(group_id)

async def send_60s(group_id: str):
    img = await get_60s_image()
    if not img:
        print('获取60s失败')
        return
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=QQMS.image(img))
