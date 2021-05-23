import asyncio
from pathlib import  Path

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

PARENT_PATH = Path(__file__).parent
IMAGE_PATH = (PARENT_PATH / 'ph.png').resolve()

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
    cmd = f'python {PARENT_PATH}/ph_logo.py {left} {right}'
    process = await asyncio.create_subprocess_shell(cmd)
    await process.wait()
    await ph.finish([
        {"type": "image", "data": {"file": f'file:///{IMAGE_PATH}'}},
    ])
    
