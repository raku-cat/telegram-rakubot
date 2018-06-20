import json
import settings
import aiofiles

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

async def getMeme(mname):
    async with aiofiles.open(memeindex, 'r') as mi:
        memefeed = json.loads(await mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    meme = mememix.get(mname)
    if meme is not None:
        return meme
    else:
        return False

