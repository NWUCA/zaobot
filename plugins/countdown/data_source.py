from datetime import date
from typing import List, Tuple

from database.group.method import get_unexpired_notices_order_by_date

async def get_countdown_list(group_id: str) -> List[Tuple[str, int, bool]]:
    cd_list = list()
    notices = await get_unexpired_notices_order_by_date(group_id)
    for notice in notices:
        cd_list.append((notice.title, (notice.date - date.today()).days, notice.fixed))
    return cd_list
