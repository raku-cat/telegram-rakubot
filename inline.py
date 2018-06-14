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

memeindex = settings.PROJECT_ROOT + '/memeindex.json'
legacy_memeindex = settings.PROJECT_ROOT + '/memes/memeindex.json'
memedir = settings.PROJECT_ROOT + '/memes/'
key = settings.getKeys()
class Inline:

    def __init__(self, msg):
        self.query_id, self.from_id, self.query_string = telepot.glance(msg, flavor='inline_query')
        self.memeslist = []
        self.tel_key = key['telegram']

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
                memelobj.append({i : await commands.send.getMeme(i)})
        for i in list(qlist.keys()):
            if regex.search(qstring, i):
                quotelobj.append({i : await commands.send.getMeme(i)})
        rnint = random.sample(range(5000), 50)
        for d, n in zip(memelobj, rnint):
            for key, value in d.items():
                memetitle = key
                memetype = value['mtype']
                file_id = value['file_id']
                thumb_id = value['thumb_id']
                async with aiohttp.ClientSession() as asession:
                    async with asession.get('https://api.telegram.org/bot' + self.tel_key + '/getFile?file_id=' + file_id) as resp:
                        file_path_json = await resp.json()
                        try:
                            file_path = file_path_json['result']['file_path']
                            #print(file_path)
                        except KeyError:
                            file_path = None
                try:
                    trumtype = file_path.split('/')[0]
                except AttributeError:
                    pass
                try:
                    memecap = value['cap']
                except KeyError:
                    memecap = ''
                if memetype == 'photo':
                    self.memeslist.append(InlineQueryResultCachedPhoto(
                        id=str(n),
                        title=memetitle,
                        photo_file_id=file_id,
                        caption=memecap
                        ))
                elif memetype == 'document':
                    if file_path is not None:
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
                        else:
                            self.memelist.append(InlineQueryResultCachedDocument(
                            id=str(n),
                            title=memetitle,
                            document_file_id=file_id,
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

