from datetime import date
from typing import Any, Callable, List, Tuple
from sqlalchemy.sql.expression import select, and_, Select, asc
from sqlalchemy.ext.asyncio import AsyncResult
from database import AsyncDatabase as AD
from database import Notice

select: Callable[[Any], Select]

async def get_countdown_list(group_id: str) -> List[Tuple[str, int, bool]]:
    async with AD.session() as session:
        async with session.begin():
            result: AsyncResult = await session.execute(
                select(Notice)
                .where(and_(
                    Notice.group_id     == group_id,
                    Notice.date         >= date.today()))
                .order_by(asc(Notice.date))
            )
    notices: List[Notice] = list(result.scalars())
    cd_list: List[Tuple[str, int]] = list()
    for notice in notices:
        cd_list.append((notice.title, (notice.date - date.today()).days, notice.fixed))
    return cd_list
