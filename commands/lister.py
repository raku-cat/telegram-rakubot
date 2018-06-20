import settings
import json
import aiofiles

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

async def getList():
    async with aiofiles.open(memeindex) as f:
        memefeed = json.loads(await f.read())
    temp = list()
    for k in memefeed.keys():
        temp.append(list(memefeed[k]))
    temp = temp[0] + temp[1]
    temp = sorted(temp)
    memlist = list()
    for i in temp:
        formatt = '- ' + i + '\n'
        memlist.append(formatt)
    memelist = ''.join(memlist)
    return memelist

