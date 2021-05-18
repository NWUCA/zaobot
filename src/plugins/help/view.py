from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

msg = """——————help——————
/zao [自称] 早
/wan [秒数] 晚
/zaoguys 早列表
/ky 考研倒计时
/chp 彩虹屁
/ask [问题] 玄学回答问题
/sxcx [缩写] 缩写查询
——————————————"""

help = on_command('help')
@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await help.finish(msg)
