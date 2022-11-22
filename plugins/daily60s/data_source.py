import httpx

url = 'https://api.vvhan.com/api/60s'

async def get_60s_image() -> bytes:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)
    if response.status_code != 200:
        return None
    return response.read()
