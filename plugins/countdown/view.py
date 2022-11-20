from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP

from .data_source import get_countdown_list

cd = on_command('cd', aliases={'countdown', '倒计时', 'djs'}, permission=GROUP, priority=5, block=True)
@cd.handle()
async def _(event: GroupMessageEvent):
    cd_list = await get_countdown_list(event.group_id)
    if not cd_list:
        return
    msg = '————倒计时————\x0a'
    for title, days, fixed in cd_list:
        msg += f'{title}: {"今" if days == 0 else days}天{"" if fixed else "左右"}\x0a'
    await cd.finish(msg[:-1])
