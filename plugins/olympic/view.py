from io import StringIO

from nonebot import on_command, get_driver
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import httpx

medal_rank = on_command('奖牌榜', aliases={'medal',})
@medal_rank.handle()
async def _(bot: Bot, event: Event, state: T_State):
    appid = get_driver().config.yike_appid
    appsecret = get_driver().config.yike_appsecret
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://apia.yikeapi.com/olympic/?appid={appid}&appsecret={appsecret}')
    data = response.json()

    if data['errcode'] != 0:
        medal_rank.finish(data['errmsg'])
    
    reply_table = tran_row(center('参赛方'), '🏅️', '🥈', '🥉', '总计')
    for d in data['list'][:10]:
        reply_table += tran_row(center(d['country']), d['jin'], d['yin'], d['tong'], d['total'])
    print(reply_table[:-1])
    await medal_rank.finish(reply_table[:-1])


def tran_row(*a) -> str:
    with StringIO() as buffer:
        print(*a, sep='\t', file=buffer)
        buffer.seek(0)
        return buffer.read()

def center(text: str, fill_char: str='．', max_len: int=6) -> str:
    return text[:max_len].center(max_len, fill_char)

"""
{
    'errcode': 0,
    'errmsg': 'success',
    'update_time': '2021-07-29 11:52:45',
    'list': [{
        'country': '中国',
        'flag': 'https://search-operate.cdn.bcebos.com/7dce3e5758a82e720ec1c7123d246616.png',
        'jin': 14,
        'yin': 6,
        'tong': 9,
        'total': 29
    }, {
        'country': '美国',
        'flag': 'https://search-operate.cdn.bcebos.com/19f0d6e267727f9846559d420a2068a6.png',
        'jin': 13,
        'yin': 13,
        'tong': 10,
        'total': 36
    }, {
        'country': '日本',
        'flag': 'https://search-operate.cdn.bcebos.com/4d04bde9a3248455c0d977e287c531e1.png',
        'jin': 13,
        'yin': 4,
        'tong': 5,
        'total': 22
    }, {
        'country': '俄罗斯奥委会',
        'flag': 'https://search-operate.cdn.bcebos.com/8c00d69be531ba4b21d5100d2a13fb8b.png',
        'jin': 7,
        'yin': 11,
        'tong': 7,
        'total': 25
    }
}
"""