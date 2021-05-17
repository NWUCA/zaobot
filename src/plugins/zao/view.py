from datetime import datetime, timedelta
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from .data_source import get_zao_boys, save_zao_boys

zao = on_command('zao')

@zao.handle()
async def _(bot: Bot, event: Event, state: T_State):
    claim = str(event.get_message()).strip() or '少年'
    zao_boys = await get_zao_boys()
    qq_id = event.get_user_id()
    if not zao_boys.__contains__(qq_id):
        zao_boys[qq_id] = datetime.now()
        await save_zao_boys(zao_boys)
        await zao.finish(f'你是第{len(zao_boys)}的{claim}。')
    if zao_boys[qq_id] is None:
        await zao.finish(f'你不是睡了吗？')
    await zao.finish(f'你不是起床过了嘛？')

# wan = on_command('wan')

# @wan.handle()
# async def _(bot: Bot, event: Event, state: T_State):
#     delay = str(event.get_message()).strip()
#     zao_boys = await get_zao_boys()
#     qq_id = event.get_user_id()
#     if not zao_boys.__contains__(qq_id):
#         await wan.finish('Pia!<(=ｏ ‵-′)ノ☆ 不起床就睡，睡死你好了～')
#     dt: datetime = zao_boys[qq_id]
#     print('dt:', dt)
#     if dt is None:
#         await wan.finish('wanwanwanwwwww')
#     # zao_boys[qq_id] = None
#     wake_time: timedelta = datetime.now() - dt
#     print(timedelta.seconds, timedelta(seconds=57))
