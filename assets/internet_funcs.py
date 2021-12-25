import aiohttp
import json
import re
import urllib.parse


async def get_response(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response = (await response.content.read()).decode('utf-8')
    return response


async def get_binary(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response = (await response.content.read())
    return response


async def get_json(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
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


async def post_json(url: str, data: dict = None, params: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, params=params) as response:
            response = (await response.json())
    return response


async def urban_define(term):
    x = await get_json(f'https://api.dictionaryapi.dev/api/v1/entries/en/{term}')
    # Thanks to CorpNewt for the idea, and his help in making this command work
    dict_object = json.loads(x)
    thing = dict_object
    define1 = thing.get('list')[0]
    word = str(define1.get('word')).title()
    definition = str(define1.get('definition'))
    example = str(define1.get('example'))

    pattern = r'\[(.+?)\]'
    result = set(re.findall(pattern, definition))
    for x in result:
        encoded = urllib.parse.quote(x)
        definition = definition.replace(f"[{x}]", f"__[{x}](https://www.urbandictionary.com/define.php?term={encoded})__")

    result2 = set(re.findall(pattern, example))
    for x in result2:
        encoded2 = urllib.parse.quote(x)
        example = example.replace(f"[{x}]", f"__[{x}](https://www.urbandictionary.com/define.php?term={encoded2})__")

    return {
        "word": word,
        "definition": definition,
        "example": example,
        "likes": define1.get('thumbs_up'),
        "dislikes": define1.get('thumbs_down'),
        "author": define1.get('author')
    } if word else None
