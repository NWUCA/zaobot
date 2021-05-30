import datetime
from typing import Union, List

from sqlalchemy import Column, DateTime, String, Boolean, update, delete, select
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.functions import func

from src.plugins._database import Base, async_session
class ZaoBoy(Base):
    __tablename__ = 'zao_boy'
    qq_id = Column(String(12), primary_key=True)
    qq_nickname = Column(String)
    zao_datetime = Column(DateTime, default=datetime.datetime.now)
    has_wan = Column(Boolean, default=False)

async def get_zao_boy(qq_id: str) -> Union[ZaoBoy, None]:
    async with async_session() as session:
        return await session.get(ZaoBoy, qq_id)

async def get_all_boys() -> List[ZaoBoy]:
    async with async_session() as session:
        result = await session.execute(select(ZaoBoy).order_by(asc(ZaoBoy.zao_datetime)))
        return list(a[0] for a in result.fetchall())

async def create_zao_boy(qq_id: str, qq_nickname: str) -> int:
    async with async_session() as session:
        async with session.begin():
            session.add(ZaoBoy(qq_id=qq_id, qq_nickname=qq_nickname))
        return (await session.execute(func.count(ZaoBoy.qq_id))).first()[0]
            
async def set_wan_boy(qq_id: str) -> None:
    async with async_session() as session:
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
