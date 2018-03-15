import settings
import commands.send
import ujson
import random

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

def getLucc():
    with open(memeindex) as f:
        memefeeds = ujson.loads(f.read())
    memf = memefeeds[random.choice(list(memefeeds.keys()))]
    luckymeme = random.choice(list(memf.keys()))
    return luckymeme
