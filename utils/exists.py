import settings
import ujson

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

def Exists(mname):
    with open(memeindex, 'r') as mi:
        memefeed = ujson.loads(mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get(i)
        mememix.update(indvmeme)
    if mname in mememix:
        return True
    else:
        return False

