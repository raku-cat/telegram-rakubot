import settings
import ujson
import asyncio
import commands
import aiofiles
import aiohttp
import telepot, telepot.aio
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle, InlineQueryResultCachedPhoto, InlineQueryResultCachedDocument, InlineQueryResultVoice, InlineQueryResultCachedGif, InlineQueryResultCachedMpeg4Gif, InlineQueryResultAudio
import regex
import random
import requests

memeindex = settings.PROJECT_ROOT + '/memeindex.json'
legacy_memeindex = settings.PROJECT_ROOT + '/memes/memeindex.json'
memedir = settings.PROJECT_ROOT + '/memes/'

class Inline:

    def __init__(self, msg, api_key):
        self.query_id, self.from_id, self.query_string = telepot.glance(msg, flavor='inline_query')
        self.memeslist = []
        self.tel_key = api_key['telegram']
 
    async def result(self):
        async with aiofiles.open(memeindex) as f:
            self.memefeed = ujson.loads(await f.read())
        qstring = self.query_string.lower()
        memelobj = []
        quotelobj = []
        mlist = self.memefeed['files']
        qlist = self.memefeed['quotes']
        for i in list(mlist.keys()):
            if regex.search(qstring, i):
                memelobj.append({i : commands.send.getMeme(i)})
        for i in list(qlist.keys()):
            if regex.search(qstring, i):
                quotelobj.append({i : commands.send.getMeme(i)})
        rnint = random.sample(range(5000), 50)
        for d, n in zip(memelobj, rnint):
            for key, value in d.items():
                memetitle = key
                memetype = value['mtype']
                file_id = value['file_id']
                thumb_id = value['thumb_id']
                async with aiohttp.ClientSession() as asession:
                    async with asession.get('https://api.telegram.org/bot' + self.tel_key + '/getFile?file_id=' + file_id) as resp:
                        file_path = await resp.json()
                        file_path = file_path['result']['file_path']
                trumtype = file_path.split('/')[0]
                #tele_file_url = 'https://api.telegram.org/file/bot' + self.tel_key + '/' + file_path
                #thumb_path = requests.get('https://api.telegram.org/bot' + self.tel_key + '/getFile?file_id=' + thumb_id).json()['result']['file_path']
                #thumb_url = 'https://api.telegram.org/file/bot' + self.tel_key + '/' + thumb_path
                #imgur_post_obj = {
                #                'image' : tele_file_url
                #            }
                #imgur_post = requests.post('https://api.imgur.com/3/upload.json', headers = {'Authorization' : 'Client-ID ' + self.img_key}, data=imgur_post_obj)
                #print(imgur_post.json())
                #if imgur_post.json()['status'] == 200:
                #    file_url = 'https://i.imgur.com/' + imgur_post.json()['data']['id'] +'.jpg'
                    #print(file_url)
                #else:
                #    return
                #print(thumb_path)
                #print(thumb_url)

                try:
                    memecap = value['cap']
                except KeyError:
                    memecap = ''
                if memetype == 'photo':
                    self.memeslist.append(InlineQueryResultCachedPhoto(
                        id=str(n),
                        title=memetitle,
                        photo_file_id=file_id,
                        #thumb_url=thumb_url,
                        caption=memecap
                        ))
                elif memetype == 'document':
                    if trumtype == 'animations':
                        if file_path.split('.')[0] == 'mp4':
                            self.memeslist.append(InlineQueryResultCachedMpeg4Gif(
                            id=str(n),
                            title=memetitle,
                            mpeg4_file_id=file_id,
                            caption=memecap
                            ))
                        else:
                            self.memeslist.append(InlineQueryResultCachedGif(
                            id=str(n),
                            title=memetitle,
                            gif_file_id=file_id,
                            caption=memecap
                            )) 
                elif memetype == 'audio':
                    self.memeslist.append(InlineQueryResultVoice(
                        id=str(n),
                        voice_url=file_url,
                        title=memetitle,
                        caption=memecap
                        ))
                else:
                    return
        rnint = random.sample(range(5000), 50)
        for q, n in zip(quotelobj, rnint):
                for key, value in q.items():
                    memetitle = key
                    memetext = value['text']
                    memeauthor = value['author']
                    self.memeslist.append(InlineQueryResultArticle(
                        id=str(n), title=memetitle,
                        input_message_content=InputTextMessageContent(
                            message_text=memetext + '\n <i>— ' + memeauthor + '</i>',
                            parse_mode='html')
            ))
                #print(memeslist)
        if len(self.memeslist) > 50:
            memeslistfinal = self.memeslist[:50]
        else:
            memeslistfinal = self.memeslist
        return { 'results' : memeslistfinal, 'cache_time' : 30 }

