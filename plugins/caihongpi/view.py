from nonebot import on_command
import httpx

chp = on_command('chp', aliases={'彩虹屁'}, priority=10, block=True)
@chp.handle()
async def _():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.shadiao.pro/chp')
    if response.status_code == 200:
        await chp.finish(response.json()['data']['text'], at_sender=True)
