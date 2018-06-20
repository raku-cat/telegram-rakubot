import settings
import json
import aiofiles

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

async def Exists(mname):
    async with aiofiles.open(memeindex, 'r') as mi:
        memefeed = json.loads(await mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    if mname in mememix:
        return True
    else:
        return False

