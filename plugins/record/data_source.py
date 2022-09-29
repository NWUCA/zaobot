from database import AsyncDatabase as AD
from database import GroupMessage

async def store_msg(qq_id:str, group_id: str, message: str):
    async with AD.session() as session:
        async with session.begin():
            session.add(GroupMessage(qq_id=qq_id, group_id=group_id, message=message))
