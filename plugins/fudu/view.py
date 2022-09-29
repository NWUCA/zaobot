import random

from nonebot.plugin import on_message
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from .model import FuDu

fu_du = FuDu(msg='')

fudu = on_message(block=False)
@fudu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global fu_du
    msg = event.get_message()
    if fu_du.msg == msg:
        fu_du.repeat += 1
    else:
        fu_du.zero(msg)
    if fu_du.has_fu_du or fu_du.repeat < 2:
        return
    if random.randint(0, max(0, 10 - fu_du.has_fu_du)) == 0:
        fu_du.has_fu_du = True
        await fudu.finish(msg)
