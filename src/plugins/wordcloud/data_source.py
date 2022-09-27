from io import StringIO
from datetime import timedelta, datetime
from sqlalchemy import select
from database import AsyncDatabase as AD
from database import GroupMessage

async def store_msg(group_id: str, msg: str):
    async with AD.session() as session:
        async with session.begin():
            session.add(GroupMessage(group_id=group_id, msg=msg))

async def fetch_msg(group_id: str, delta: timedelta) -> StringIO:
    async with AD.engine().connect() as conn:
        async_result = await conn.stream(
            select(GroupMessage)
            .where(
                GroupMessage.group_id == group_id
                and GroupMessage.datetime >= datetime.now() - delta
            )
        )
        result = await async_result.columns('msg').all()
        msg_buffer = StringIO()
        for row in result:
            msg_buffer.write(row[0])
        msg_buffer.seek(0)
        return msg_buffer
