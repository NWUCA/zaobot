from io import StringIO
from datetime import timedelta, datetime
from sqlalchemy import select
from database import async_engine, GroupMessage

from database.group.method import get_group_messages

async def fetch_msg(group_id: str, delta: timedelta) -> StringIO:
    result = await get_group_messages(group_id, delta)
    msg_buffer = StringIO()
    for row in result:
        msg_buffer.write(row[0])
    msg_buffer.seek(0)
    return msg_buffer
