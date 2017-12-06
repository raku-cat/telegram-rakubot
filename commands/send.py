import json
import settings

memeindex = settings.PROJECT_ROOT + '/memeindex.json'
legacy_memeindex = settings.PROJECT_ROOT + 'memeindex.json'

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

