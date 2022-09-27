from typing import Union, List
from sqlalchemy import update, delete, select
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.functions import func

from database import AsyncDatabase as AD
from database import ZaoBoy

async def get_zao_boy(qq_id: str) -> Union[ZaoBoy, None]:
    async with AD.session() as session:
        return await session.get(ZaoBoy, qq_id)

async def get_all_boys() -> List[ZaoBoy]:
    async with AD.session() as session:
        result = await session.execute(select(ZaoBoy).order_by(asc(ZaoBoy.zao_datetime)))
        return list(a[0] for a in result.fetchall())

async def create_zao_boy(qq_id: str, qq_nickname: str) -> int:
    async with AD.session() as session:
        async with session.begin():
            session.add(ZaoBoy(qq_id=qq_id, qq_nickname=qq_nickname))
        return (await session.execute(func.count(ZaoBoy.qq_id))).first()[0]
            
async def set_wan_boy(qq_id: str) -> None:
    async with AD.session() as session:
        async with session.begin():
            await session.execute(
                update(ZaoBoy)
                .values(has_wan=True)
                .where(ZaoBoy.qq_id == qq_id)
            )
            
async def clear_zao_boys() -> None:
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(ZaoBoy))
