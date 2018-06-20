import json
import settings
import aiofiles

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

async def deleteMeme(mname):
    async with aiofiles.open(memeindex) as f:
        memefeed = json.loads(await f.read())
    try:
        del memefeed['files'][mname]
    except KeyError:
        try:
            del memefeed['quotes'][mname]
        except KeyError:
            return False
    async with aiofiles.open(memeindex, 'w') as f:
        await f.write(json.dumps(memefeed))
    return True

