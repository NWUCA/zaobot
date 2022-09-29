import base64
import sys
import asyncio
from pathlib import  Path

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from .util import safe

PARENT_PATH = Path(__file__).parent
IMAGE_PATH = (PARENT_PATH / 'ph.png').resolve()
lock = asyncio.Lock()
encoding = 'gbk' if (sys.platform == 'win32') else 'utf-8'

ph_parser = ArgumentParser()
ph_parser.add_argument('left')
ph_parser.add_argument('right')

ph = on_shell_command('ph', parser=ph_parser)
@ph.handle()
async def _(bot: Bot, event: Event, state: T_State):
    left = getattr(state['args'], 'left', None)
    right = getattr(state['args'], 'right', None)
    if not left or not right:
        return

    process = await asyncio.create_subprocess_shell(
        f'python {PARENT_PATH}/ph_logo.py',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate(
        f'{left}\n{right}\n'.encode(encoding)
    )
    img_base64 = 'base64://' + stdout.decode(encoding).strip()[2:-1]
    await process.wait()
    await ph.finish([
        {"type": "image", "data": {"file": img_base64}},
    ])
