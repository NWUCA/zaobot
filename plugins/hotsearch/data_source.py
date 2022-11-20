from typing import Dict, List
from datetime import date
import httpx

url = 'https://weibo.com/ajax/side/hotSearch'

async def get_weibo_hot_search() -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        return []
    return response.json()['data']
