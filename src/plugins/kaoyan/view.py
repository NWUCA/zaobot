from datetime import datetime

from nonebot import on_command
from nonebot.rule import ArgumentParser
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg

from .data_source import get_ky_date, set_ky_date

ky = on_command('ky')
@ky.handle()
async def _(matcher: Matcher):
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
setky_parser.add_argument('month', metavar='M', type=int, help='月')
setky_parser.add_argument('day',   metavar='D', type=int, help='日')

setky = on_command("设置考研日期", priority=1, block=True, permission=GROUP_OWNER|GROUP_ADMIN)#, permission=SUPERUSER)


@setky.handle()
async def _(arg: Message = CommandArg()):
    month, day = map(int, arg.extract_plain_text().strip().split('/'))
    if not (month and day):
        return
    try:
        set_ky_date(month, day)
    except ValueError:
        await setky.finish('管理员带头搞事情？')
    ky_date = get_ky_date()
    await setky.finish(f'已考研日期设置为{ky_date}')
