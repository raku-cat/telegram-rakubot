import settings
import ujson

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

def getList():
    with open(memeindex) as f:
        memefeed = ujson.loads(f.read())
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

