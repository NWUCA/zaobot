from io import StringIO
from datetime import timedelta, datetime, date
from typing import Any, Callable, List
from sqlalchemy.sql.expression import select, and_, Select, asc
from sqlalchemy.ext.asyncio import AsyncResult
from database import Database
from database.group.model import GroupNotice, GroupMessage

select: Callable[[Any], Select]

async def get_unexpired_notices_order_by_date(group_id: str) -> List[GroupNotice]:
    async with Database.async_session() as session:
        async with session.begin():
            result: AsyncResult = await session.execute(
                select(GroupNotice)
                .where(and_(
                    GroupNotice.group_id == group_id,
                    GroupNotice.date     >= date.today()))
                .order_by(asc(GroupNotice.date))
            )
    return list(result.scalars())

async def store_group_msg(qq_id:str, group_id: str, message_id:str, message: str):
    async with Database.async_session() as session:
        async with session.begin():
            await session.add(GroupMessage(
                qq_id=qq_id,
                group_id=group_id,
                message_id=message_id,
                message=message,
            ))

async def get_group_messages(group_id: str, delta: timedelta) -> StringIO:
    async with Database.async_engine().connect() as conn:
        async_result = await conn.stream(
            select(GroupMessage)
            .where(
                GroupMessage.group_id == group_id
                and GroupMessage.datetime >= datetime.now() - delta
            )
        )
    return await async_result.columns('msg').all()
