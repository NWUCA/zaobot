import asyncio
from pathlib import Path

from nonebot import on_message, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import GROUP

from .tables import fetch_msg, store_msg

PARENT_PATH = Path(__file__).parent

ciyun_parser = ArgumentParser()
ciyun_parser.add_argument('delta', nargs='?', default=7, type=int, help='距今多少天')
ciyun = on_shell_command('ciyun', parser=ciyun_parser, permission=GROUP)
@ciyun.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg_buffer = await fetch_msg(event.group_id, state['args'].delta)
    process = await asyncio.create_subprocess_shell(
        f'python {PARENT_PATH}/word_cloud.py',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate(
        msg_buffer.read().encode()
    )
    msg_buffer.close()
    # print(stdout.decode())
    img_base64 = 'base64://' + stdout.decode().strip()[2:-1]
    await process.wait()
    await ciyun.finish([
        {"type": "image", "data": {"file": img_base64}},
    ])


store = on_message(block=False, permission=GROUP, priority=10)
@store.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    text = event.get_plaintext().strip()
    if text:
        await store_msg(event.group_id, text)
