from io import StringIO
from datetime import timedelta, datetime

from sqlalchemy import Column, select
from sqlalchemy.sql.sqltypes import DateTime, String, Integer

from src.plugins._database import Base, engine, async_session

class GroupMessage(Base):
    __tablename__ = 'group_message'
    id = Column(Integer, primary_key=True)
    group_id = Column(String(12), index=True)
    msg = Column(String)
    datetime = Column(DateTime, default=datetime.now)

async def store_msg(group_id: str, msg: str):
    async with async_session() as session:
        async with session.begin():
            session.add(GroupMessage(group_id=group_id, msg=msg))

async def fetch_msg(group_id: str, delta: timedelta) -> StringIO:
    async with engine.connect() as conn:
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


