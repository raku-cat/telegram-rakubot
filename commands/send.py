import json
import settings

memeindex = settings.PROJECT_ROOT + '/memeindex.json'
legacy_memeindex = settings.PROJECT_ROOT + '/memes/memeindex.json'
memedir = settings.PROJECT_ROOT + '/memes/'

def getMeme(mname):
    with open(memeindex, 'r') as mi:
        memefeed = json.load(mi)
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    meme = mememix.get(mname)
    if meme is not None:
        return meme
    else:
        return False
def getLegacyMeme(mname):
    with open(legacy_memeindex, 'r') as mi:
        memefeed = json.load(mi)
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    meme = mememix.get(mname)
    if meme is not None:
        with open(memedir + meme['filename'], 'rb') as mef:
            meme['file_id'] = mef.read()
        print('salsa')
        return meme
    else:
        return False

