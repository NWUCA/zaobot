from urllib.parse import quote

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

choyen_parser = ArgumentParser()
choyen_parser.add_argument('top')
choyen_parser.add_argument('bottom', nargs='?', default='欲しい!')

choyen = on_shell_command('choyen', aliases={'5000'}, parser=choyen_parser)
@choyen.handle()
async def _(bot: Bot, event: Event, state: T_State):
    top = getattr(state['args'], 'top', None)
    bottom = getattr(state['args'], 'bottom', None)
    if not top or not bottom:
        return
    top = quote(top)
    bottom = quote(bottom)
    print(top, bottom)
    await choyen.finish([
        {"type": "image", "data": {
            "file": f'http://zhangjunbo.top:18003/api/v1/gen?top={top}&bottom={bottom}'
        }},
    ])


