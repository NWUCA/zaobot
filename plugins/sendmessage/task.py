import nonebot

from database.schedule.decorator import task_register

@task_register(key='推送自定义消息')
async def _(group_id: str, addition: str):
    if not isinstance(addition, str):
        return
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id, message=addition)
