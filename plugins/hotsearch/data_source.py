import aiofiles
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from typing import Dict, List
import httpx

from plugins.playwright import get_new_page, get_playwright

url = 'https://weibo.com/ajax/side/hotSearch'

async def get_weibo_hot_search() -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        return []
    return response.json()['data']

async def gen_weibo_hot_search_image() -> bytes:
    raw_data = await get_weibo_hot_search()

    time_str = datetime.now().strftime('%m月%d日 %H:%M')
    data = list()
    data.append({
        'index': 'G',
        'title': raw_data['hotgov']['word'],
        'num': None,
        'icon': raw_data['hotgov'].get('small_icon_desc'),
        'icon_color': raw_data['hotgov'].get('small_icon_desc_color'),
    })
    for index, rs in enumerate(raw_data['realtime'][:10], 1):
        data.append({
            'index': index,
            'title': rs['word'],
            'num': rs['num'],
            'icon': rs.get('small_icon_desc'),
            'icon_color': rs.get('small_icon_desc_color'),
        })

    

    async with aiofiles.open(Path(__file__).parent / 'template/hotsearch.html', 'r') as f:
        html_template = await f.read()

    template = Template(html_template, enable_async=True)
    html = await template.render_async(time=time_str, data=data)

    async with get_new_page(**get_playwright().devices['iPhone 12']) as page:
        await page.set_content(html)
        return await page.screenshot(timeout=60_000, full_page=True)

