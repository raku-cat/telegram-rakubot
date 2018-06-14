import settings
import ujson
import aiofiles

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

async def getMemeById(memeid):
    async with aiofiles.open(memeindex, 'r') as mi:
        memefeed = ujson.loads(await mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get('files')
        mememix.update(indvmeme)
    for memenames, values in mememix.items():
        if values['file_id'] == memeid:
            return memenames

async def getMemeByText(memetext):
    async with aiofiles.open(memeindex, 'r') as mi:
        memefeed = ujson.loads(await mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get('quotes')
        mememix.update(indvmeme)
        memesplit = memetext.splitlines()
        memenoauth = "".join(memesplit[:-1])
    for memenames, values in mememix.items():
        if values['text'] == memenoauth:
            return memenames

