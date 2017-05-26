#!/usr/bin/env python3
from ffmpy import FFmpeg
import magic
import sys
import json
import os

memedir = sys.path[0] + '/memes/'
memeindex = memedir + 'memeindex.json'

def oggconv():
    with open(memeindex) as f:
        memefeeds = json.load(f)
    for keys, values in memefeeds['files'].items():
        if values['mtype'] == 'audio':
            if magic.Magic(mime=True).from_file(memedir + values['filename']) != 'audio/ogg':
                memespec = memedir + values['filename']
                os.rename(memespec, memedir + 'temp_' + values['filename'])
                ff = FFmpeg(
                    inputs={memedir + 'temp_' + values['filename']: '-loglevel panic -y'},
                    outputs={memespec: '-acodec libopus -b:a 48k -vbr on -compression_level 10'}
                    )
                #print(ff.cmd)
                ff.run()
                os.remove(memedir + 'temp_' + values['filename'])
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
