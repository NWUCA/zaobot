import pickle
from io import BytesIO
from pathlib import Path
from datetime import datetime
from typing import Dict, Union, NewType

from nonebot import require
import aiofiles

zao_boys_file = Path(__file__).parent / 'zao_boys~'
if not zao_boys_file.exists():
    with open(zao_boys_file, 'wb') as f:
        pickle.dump({}, f)

ZaoBoys = NewType('ZaoBoys', Dict[str, Union[datetime, None]])

async def get_zao_boys() -> ZaoBoys:
    async with aiofiles.open(zao_boys_file, 'rb') as f:
        with BytesIO(await f.read()) as buffer:
            zao_boys: ZaoBoys = pickle.load(buffer)
    return zao_boys

async def save_zao_boys(zao_boy: ZaoBoys) -> None:
    async with aiofiles.open(zao_boys_file, 'wb') as f:
        with BytesIO() as buffer:
            pickle.dump(zao_boy, buffer)
            await f.write(buffer.getbuffer())

scheduler = require('nonebot_plugin_apscheduler').scheduler

@scheduler.scheduled_job('cron', hour=4)
async def _():
    print('凌晨四点清除zao boys名单')
    await save_zao_boys({})
