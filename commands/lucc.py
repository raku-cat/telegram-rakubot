import settings
import commands.send
import ujson
import random
import aiofiles

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

async def getLucc():
    async with aiofiles.open(memeindex) as f:
        memefeeds = ujson.loads(await f.read())
    memf = memefeeds[random.choice(list(memefeeds.keys()))]
    luckymeme = random.choice(list(memf.keys()))
    return luckymeme
