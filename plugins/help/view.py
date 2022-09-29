from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

msg = """——————help——————
/zao [自称] 早
/wan [分钟] 晚
/zaoguys 早列表
/ky 考研倒计时
/chp 彩虹屁
/ask [问题] 玄学回答问题
/sxcx [缩写] 缩写查询
/ph <左> <右> 生成ph logo
/5000 <上> [下] 5000兆元生成
——————————————"""

help = on_command('help')
@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await help.finish(msg)
