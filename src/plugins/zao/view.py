from datetime import datetime
from nonebot import on_command, on_shell_command, require
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER

from .tables import clear_zao_boys, get_zao_boy, create_zao_boy, set_wan_boy, get_all_boys

zao = on_command('zao')
@zao.handle()
async def _(bot: Bot, event: Event, state: T_State):
    claim = str(event.get_message()).strip() or '少年'
    qq_id = event.get_user_id()
    zao_boy = await get_zao_boy(qq_id)
    if zao_boy is None:
        count = await create_zao_boy(qq_id, event.sender.nickname)
        await zao.finish(f'你是第{count}起床的{claim}。', at_sender=True)
    if zao_boy.has_wan:
        await zao.finish(f'你不是睡了吗？', at_sender=True)
    await zao.finish(f'你不是起床过了嘛？', at_sender=True)

wan_parser = ArgumentParser()
wan_parser.add_argument('delay', nargs='?', default=0, type=int, help='再过多少分钟睡觉')
wan = on_shell_command('wan', parser=wan_parser)
@wan.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qq_id = event.get_user_id()
    zao_boy = await get_zao_boy(qq_id)
    if zao_boy is None:
        await wan.finish('Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～', at_sender=True)
    if zao_boy.has_wan:
        await wan.finish('睡着了的人是不能说话的哦（准备物理晚安）', at_sender=True)
    
    delay = getattr(state['args'], 'delay', 0)
    if delay < 0:
        await wan.finish('等你进入五维世界，这条指令没准儿可行', at_sender=True)
    elif delay > 264 * 60 + 24:
        await wan.finish('据维基百科记载，人类最长不睡觉时间的世界纪录是264.4小时，请保重', at_sender=True)
    await set_wan_boy(qq_id)

    wake_seconds: int = (datetime.now() - zao_boy.zao_datetime).seconds + delay * 60
    wake_minutes = wake_seconds // 60
    wake_hours = wake_minutes // 60
    wake_seconds %= 60
    wake_minutes %= 60
    msg = f'将在{delay}分钟后睡觉，' if delay else ''
    msg += f'今天共清醒{wake_hours}小时{wake_minutes}分{wake_seconds}秒，辛苦了。'
    await wan.finish(msg, at_sender=True)

zaoguys = on_command('zaoguys')
@zaoguys.handle()
async def _(bot: Bot, event: Event, state: T_State):
    zao_boys = await get_all_boys()
    print(zao_boys)
    msg = ''
    for index, boy in enumerate(zao_boys, 1):
        msg += f'{index}. {boy.qq_nickname}, {boy.zao_datetime.hour}:{boy.zao_datetime.minute}\x0a'
    await zaoguys.finish(msg[:-1])

scheduler = require('nonebot_plugin_apscheduler').scheduler
@scheduler.scheduled_job('cron', hour=4)
async def _():
    print('凌晨四点清除zao boys名单')
    await clear_zao_boys()

clearzao = on_command('clearzao', permission=GROUP_OWNER|GROUP_ADMIN)
@clearzao.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await clear_zao_boys()
    await clearzao.finish('已清除zao名单', at_sender=True)
