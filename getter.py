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
    memedict = { mname : mlist[mname] }
    return memedict
def quotes(qname):
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    qlist = memefeed['quotes']
    quotedict = { qname : qlist[qname] }
    return quotedict
