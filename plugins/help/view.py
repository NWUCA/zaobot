from nonebot import on_command

help = on_command('help', aliases={'帮助', '?', 'git', 'github'}, priority=2, block=True)
@help.handle()
async def _():
    await help.finish('https://github.com/NWUCA/zaobot/', at_sender=True)
