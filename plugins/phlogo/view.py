import sys
import asyncio
from pathlib import Path

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from nonebot.params import CommandArg

from .util import safe

PARENT_PATH = Path(__file__).parent
IMAGE_PATH = (PARENT_PATH / 'ph.png').resolve()
lock = asyncio.Lock()
encoding = 'gbk' if (sys.platform == 'win32') else 'utf-8'

ph = on_command('ph', aliases={'pornhub'}, priority=5, block=True)
@ph.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split()
    if len(args) != 2:
        return
    left, right = args
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
    await ph.finish(MessageSegment.image(img_base64))
