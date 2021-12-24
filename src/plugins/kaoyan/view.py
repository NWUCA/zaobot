from datetime import datetime, date

from nonebot import on_command, on_shell_command, permission
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER

from .data_source import get_ky_date, set_ky_date

ky = on_command('ky')
@ky.handle()
async def _(bot: Bot, event: Event, state: T_State):
    ky_date = get_ky_date()
    now = datetime.now().date()
    countdown = (ky_date - now).days
    if -1 <= countdown <= 0:
        await ky.finish('今天就是考研的日子，加油！')
    if countdown < -1:
        set_ky_date(ky_date.month, ky_date.day)
        ky_date = get_ky_date()
    await ky.finish(f'距离{ky_date.year}年度研究生考试还有{countdown}天')

setky_parser = ArgumentParser()
setky_parser.add_argument('month', type=int, help='月')
setky_parser.add_argument('day', type=int, help='日')

setky = on_shell_command('setky', parser=setky_parser, permission=GROUP_OWNER|GROUP_ADMIN)
@setky.handle()
async def _(bot: Bot, event: Event, state: T_State):
    month = getattr(state['args'], 'month', None)
    day = getattr(state['args'], 'day', None)
    if not (month and day):
        return
    try:
        set_ky_date(month, day)
    except ValueError:
        await ky.finish('管理员带头搞事情？')
    ky_date = get_ky_date()
    await ky.finish(f'已考研日期设置为{ky_date}')
