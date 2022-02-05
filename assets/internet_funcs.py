import aiohttp


async def get_response(url: str, **kwargs):
    async with aiohttp.ClientSession(**kwargs) as session:
        async with session.get(url) as response:
            response = (await response.content.read()).decode('utf-8')
    return response


async def get_binary(url: str, **kwargs):
    async with aiohttp.ClientSession(**kwargs) as session:
        async with session.get(url) as response:
            response = (await response.content.read())
    return response


async def get_json(url: str, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, **kwargs) as response:
            response = (await response.json())
    return response


async def post(url: str, data: dict = None, params: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, params=params) as response:
            response = (await response.content.read()).decode('utf-8')
    return response


async def post_binary(url: str, data: dict = None, params: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, params=params) as response:
            response = (await response.content.read())
    return response


async def post_json(url: str, headers: dict = None, data: dict = None, params: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data, params=params) as response:
            response = (await response.json())
    return response
