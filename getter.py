#!/usr/bin/env python3
import sys
import json
import os

memedir = sys.path[0] + '/memes/'
memeindex = memedir + 'memeindex.json'

def files(mname):
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    mlist = memefeed['files']
    print(mname)
    keys = mname
    mdict = {x:mlist[x] for x in keys}
    return memedict
