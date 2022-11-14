from datetime import datetime
from typing import Any, Callable, Union, List
from sqlalchemy.sql.expression import asc, select, update, and_, Select, Update
from sqlalchemy.sql.functions import func, Function
from sqlalchemy.ext.asyncio import AsyncResult

from database import AsyncDatabase as AD
from database.zao.model import ZaoGuy

select: Callable[[Any], Select]
update: Callable[[Any], Update]
func: Function

async def get_zao_guy(qq_id: str, group_id: str, zao_from: datetime, zao_to: datetime) -> Union[ZaoGuy, None]:
    async with AD.session() as session:
        async with session.begin():
            result: AsyncResult = await session.execute(
                select(ZaoGuy)
                .where(and_(
                    ZaoGuy.qq_id        == qq_id,
                    ZaoGuy.group_id     == group_id,
                    ZaoGuy.zao_datetime >= zao_from,
                    ZaoGuy.zao_datetime <  zao_to))
            )
    return result.scalars().first()

async def get_zao_guys(group_id: str, zao_from: datetime, zao_to: datetime) -> List[ZaoGuy]:
    async with AD.session() as session:
        async with session.begin():
            result: AsyncResult = await session.execute(
                select(ZaoGuy)
                .where(and_(
                    ZaoGuy.group_id     == group_id,
                    ZaoGuy.zao_datetime >= zao_from,
                    ZaoGuy.zao_datetime <  zao_to))
                .order_by(asc(ZaoGuy.zao_datetime))
            )
    return list(result.scalars().all())

async def get_zao_guys_count(group_id: str, zao_from: datetime, zao_to: datetime) -> int:
    async with AD.session() as session:
        async with session.begin():
            result: AsyncResult = await session.execute(
                select(func.count(ZaoGuy.qq_id))
                .where(and_(
                    ZaoGuy.group_id     == group_id,
                    ZaoGuy.zao_datetime >= zao_from,
                    ZaoGuy.zao_datetime <  zao_to))
            )
    return result.scalar_one()

async def create_zao_guy(qq_id: str, group_id: str, nickname: str) -> int:
    async with AD.session() as session:
        async with session.begin():
            session.add(ZaoGuy(qq_id=qq_id, group_id=group_id, nickname=nickname))

async def set_wan_guy(
        qq_id: str,
        group_id: str,
        zao_from: datetime,
        zao_to: datetime,
        wan_datetime: datetime) -> None:

    async with AD.session() as session:
        async with session.begin():
            await session.execute(
                update(ZaoGuy)
                .where(and_(
                    ZaoGuy.qq_id        == qq_id,
                    ZaoGuy.group_id     == group_id,
                    ZaoGuy.zao_datetime >= zao_from,
                    ZaoGuy.zao_datetime <  zao_to))
                .values(wan_datetime=wan_datetime)
            )
