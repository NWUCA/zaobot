from datetime import datetime, timedelta
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP, Event
from nonebot.params import CommandArg

from .data_source import (
    ZaoGuy,
    get_zao_guy,
    get_zao_guys,
    get_zao_guys_count,
    create_zao_guy,
    set_wan_guy,
    get_yesterday_4_clock,
)

zao = on_command('zao', permission=GROUP, priority=5, block=True)
@zao.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    claim = arg.extract_plain_text().strip() or '少年'
    # claim = str(event.get_message()).strip() or '少年'
    uid      = event.user_id
    gid      = event.group_id
    nickname = event.sender.card or event.sender.nickname
    zao_from = get_yesterday_4_clock()
    zao_to   = zao_from + timedelta(days=1, minutes=5)

    zao_boy: ZaoGuy = await get_zao_guy(uid, gid, zao_from, zao_to)
    if zao_boy is None:
        await create_zao_guy(uid, gid, nickname)
        count = await get_zao_guys_count(gid, zao_from, zao_to)
        await zao.finish(f'你是第{count}起床的{claim}。', at_sender=True)
    
    if zao_boy.wan_datetime is not None:
        await zao.finish(f'你不是睡了吗？', at_sender=True)

    await zao.finish(f'你不是起床过了嘛？', at_sender=True)

wan = on_command('wan', permission=GROUP, priority=5)
@wan.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    uid      = event.user_id
    gid      = event.group_id
    zao_from = get_yesterday_4_clock()
    zao_to   = zao_from + timedelta(days=1, minutes=5)
    now      = datetime.now()
    delay    = arg.extract_plain_text().strip()
    delay    = int(delay) if delay.isdigit() else 0

    zao_guy: ZaoGuy = await get_zao_guy(uid, gid, zao_from, zao_to)
    if zao_guy is None:
        await wan.finish('Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～', at_sender=True)
    if zao_guy.wan_datetime is not None:
        await wan.finish('睡着了的人是不能说话的哦（准备物理晚安）', at_sender=True)

    if delay < 0:
        await wan.finish('等你进入五维世界，这条指令没准儿可行', at_sender=True)
    elif delay > 264 * 60 + 24:
        await wan.finish('据维基百科记载，人类最长不睡觉时间的世界纪录是264.4小时，请保重', at_sender=True)
    await set_wan_guy(uid, gid, zao_from, zao_to, now)

    wake_seconds: int = (now - zao_guy.zao_datetime).seconds + delay * 60
    wake_minutes = wake_seconds // 60
    wake_hours = wake_minutes // 60
    wake_seconds %= 60
    wake_minutes %= 60
    msg = f'将在{delay}分钟后睡觉，' if delay else ''
    msg += f'今天共清醒{wake_hours}小时{wake_minutes}分{wake_seconds}秒，辛苦了。'
    await wan.finish(msg, at_sender=True)

zaoguys = on_command('zaoguys', priority=5)
@zaoguys.handle()
async def _(bot: Bot, event: Event, state: T_State):
    zao_from = get_yesterday_4_clock()
    zao_to   = zao_from + timedelta(days=1, minutes=5)
    zao_guys = await get_zao_guys(event.group_id, zao_from, zao_to)
    msg = ''
    for index, boy in enumerate(zao_guys, 1):
        msg += f'{index}. {boy.nickname}, {boy.zao_datetime.hour}:{boy.zao_datetime.minute}\x0a'
    await zaoguys.finish(msg[:-1])

