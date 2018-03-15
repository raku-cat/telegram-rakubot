import settings
import ujson

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

def getMemeById(memeid):
    with open(memeindex, 'r') as mi:
        memefeed = ujson.loads(mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get('files')
        mememix.update(indvmeme)
    for memenames, values in mememix.items():
        if values['file_id'] == memeid:
            return memenames

def getMemeByText(memetext):
    with open(memeindex, 'r') as mi:
        memefeed = ujson.loads(mi.read())
    mememix = {}
    for i in memefeed.keys():
        indvmeme = memefeed.get('quotes')
        mememix.update(indvmeme)
        memesplit = memetext.splitlines()
        memenoauth = "".join(memesplit[:-1])
    for memenames, values in mememix.items():
        if values['text'] == memenoauth:
            return memenames

