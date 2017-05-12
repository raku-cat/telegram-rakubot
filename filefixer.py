#/usr/bin/env python3
from ffmpy import FFmpeg
import magic
import sys
import json
import os

memedir = sys.path[0] + '/memes/'
memeindex = memedir + 'memeindex.json'

def oggconv():
    with open(memeindex) as f:
        memefeeds = json.loads(f.read())
        for keys, values in memefeeds['files'].items():
            if values['mtype'] == 'audio':
                if magic.Magic(mime=True).from_file(memedir + values['filename']) != 'audio/ogg':
                   ff = FFmpeg(
                        inputs={memedir + values['filename']: '-loglevel panic -y'},
                        outputs={memedir + values['filename']: '-acodec libopus'}
                        )
                   #print(ff.cmd)
                   ff.run()
def mp4thumb():
    with open(memeindex) as f:
        memefeeds = json.loads(f.read())
        for keys, values in memefeeds['files'].items():
            if values['mtype'] == 'video':
                if not os.path.exists(memedir + 't_' + values['filename'] + '.jpg'):
                    ff = FFmpeg(
                        inputs={memedir + values['filename']: '-loglevel panic -y -ss 00:00:00'},
                        outputs={memedir + 't_' + values['filename'] + '.jpg': '-vframes 1'}
                        )
                    #print(ff.cmd)
                    ff.run()
