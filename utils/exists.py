import settings
import json

memeindex = settings.PROJECT_ROOT + '/memeindex.json'
legacy_memeindex = settings.PROJECT_ROOT + '/memes/memeindex.json'

def Exists(mname):
    with open(memeindex, 'r') as mi:
        memefeed = json.load(mi)
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    if mname in mememix:
        return True
    else:
        return False
def legacyExists(mname):
    with open(legacy_memeindex, 'r') as mi:
        memefeed = json.load(mi)
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    if mname in mememix:
        return True
    else:
        return False
    
