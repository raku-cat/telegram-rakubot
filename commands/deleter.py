import ujson
import settings

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

def deleteMeme(mname):
    with open(memeindex) as f:
        memefeed = ujson.loads(f.read())
    try:
        del memefeed['files'][mname]
    except KeyError:
        try:
            del memefeed['quotes'][mname]
        except KeyError:
            return False
    with open(memeindex, 'w') as f:
        ujson.dump(memefeed, f, indent=2)
    return True

