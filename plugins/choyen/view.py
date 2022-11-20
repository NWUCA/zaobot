import sys
import asyncio
from pathlib import Path

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from nonebot.params import CommandArg

PARENT_PATH = Path(__file__).parent
encoding = 'gbk' if (sys.platform == 'win32') else 'utf-8'

choyen = on_command('choyen', aliases={'5000'}, priority=5, block=True)
@choyen.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split()
    if len(args) > 2:
        return
    top = '5000兆円' if len(args) == 0 else args[0]
    bottom = '欲しい!' if len(args) <= 1 else args[1]

    process = await asyncio.create_subprocess_shell(
        f'python {PARENT_PATH}/generator.py',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate(
        f'{top}\n{bottom}\n'.encode(encoding)
    )
    img_base64 = 'base64://' + stdout.decode(encoding).strip()[2:-1]
    await process.wait()
    await choyen.finish(MessageSegment.image(img_base64))



