#!/usr/bin/env python3
import sys
import telepot, telepot.aio
import asyncio, aiofiles, aiohttp
import datetime
import os
import random
import regex
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, InlineQueryResultVideo, InlineQueryResultVoice, InlineQueryResultGif, InlineQueryResultMpeg4Gif, InlineQueryResultAudio
import filefixer
import getter
from threading import Lock
import base64
import json
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
import requests


with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
bot = telepot.aio.Bot(key['telegram'])

DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')



async def on_command(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    #print(telepot.flavor(msg))
    #print(chat_type, content_type, chat_id)
    from_id = msg['from']['id']
    #print(msg)
    if content_type == 'voice':
        print(msg)
        file_id = msg['voice']['file_id']
        file_path = await bot.getFile(file_id)
        file_url = 'https://api.telegram.org/file/bot' + key['telegram'] + '/' + file_path['file_path']
        print(file_url)
        namevar = datetime.datetime.now().strftime("%Y%m%d%H%M%f") + '.ogg'
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as r:
                if r.status == 200:
                    async with aiofiles.open(namevar, 'wb') as f:
                        while True:
                            chunk = await r.content.read(128)
                            if not chunk:
                                break
                            await f.write(chunk)
        print(speechtotext(namevar))



def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build(
        'speech', 'v1', http=http, discoveryServiceUrl=DISCOVERY_URL)


def speechtotext(speech_file):
    """Transcribe the given audio file.

    Args:
        speech_file: the name of the audio file.
    """
    with open(speech_file, 'rb') as speech:
        speech_content = base64.b64encode(speech.read())

    service = get_speech_service()
    print(speech_content)
    service_request = service.speech().syncrecognize(
        body={
            'config': {
                'encoding': 'OGG_OPUS',  # raw 16-bit signed LE samples
                'sampleRate': 16000,  # 16 khz
                'languageCode': 'en-US',  # a BCP-47 language tag
            },
            'audio': {
                'content': speech_content.decode('UTF-8')
                }
            })
    response = service_request.execute()
    return(json.dumps(response))

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot,on_command).run_forever())
print('Started...')
loop.run_forever()
