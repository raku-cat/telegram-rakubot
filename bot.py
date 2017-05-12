#!/usr/bin/env python3
import sys
import telepot, telepot.aio
import asyncio, aiofiles, aiohttp
import json
import datetime
import os
import random
import regex
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, InlineQueryResultVideo, InlineQueryResultVoice, InlineQueryResultGif, InlineQueryResultMpeg4Gif, InlineQueryResultAudio
import filefixer

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
bot = telepot.aio.Bot(key['telegram'])
baseurl = key['baseurl']
memedir = sys.path[0] + '/memes/'
if not os.path.exists(memedir):
    os.makedirs(memdir)
memeindex = memedir + 'memeindex.json'
if not os.path.exists(memeindex):
    with open(memeindex, 'w') as f:
        json.dump({'files' : {}, 'quotes' : {}}, f)

filefixer.oggconv()
filefixer.mp4thumb()

async def on_command(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    #print(telepot.flavor(msg))
    #print(chat_type, content_type, chat_id)
    from_id = msg['from']['id']
    #print(msg)
    try:
        botcom = msg['entities'][0]['type']
        if not botcom == 'bot_command':
            return
    except KeyError:
        pass
    if content_type == 'text':
        try:
            reply = msg['reply_to_message']
            reply_id = reply['message_id']
        except KeyError:
            reply_id = 'None'
        command = msg['text'].lower()
        if command.startswith('/store'):
            await bot.sendChatAction(chat_id, 'typing')
            try:
                mem = command.split(' ', 1)[1]
            except IndexError:
                await bot.sendMessage(chat_id, 'Expected second argument as name `/store <name>`', parse_mode='Markdown')
                return
            try:
                if reply:
                    try:
                        file_id = reply['audio']['file_id']
                        mtype = 'audio'
                    except KeyError:
                        try:
                            file_id = reply['photo'][-1]['file_id']
                            mtype = 'photo'
                            try:
                                caption = reply['caption']
                            except KeyError:
                                caption = ''
                        except KeyError:
                            try:
                                file_id = reply['document']['file_id']
                                dmtye = reply['document']['mime_type'].split('/')[0]
                                if dmtye == 'audio':
                                    mtype = 'audio'
                                elif dmtye == 'video':
                                    mtype = 'video'
                                    try:
                                        caption = reply['caption']
                                    except KeyError:
                                        caption = ''
                            except KeyError:
                                try:
                                    reply['chat']
                                    authname = '@' + reply['from']['username']
                                    quotetext = reply['text']
                                    mtype = 'quote'
                                except KeyError:
                                    try:
                                        file_id = reply['voice']['file_id']
                                        mtype = 'audio'
                                    except KeyError:
                                        await bot.sendMessage(chat_id, 'Idk what that is, i can\'t grab it')
                                        return
                    async with aiofiles.open(memeindex) as f:
                        memefeed = json.loads(await f.read())
                    try:
                        memefeed['files'][mem]
                        await bot.sendMessage(chat_id, 'Mem already exist :V', reply_to_message_id=msg_id)
                        return
                    except KeyError:
                        try:
                            memefeed['quotes'][mem]
                            await bot.sendMessage(chat_id, 'Mem already exist :V', reply_to_message_id=msg_id)
                            return
                        except KeyError:
                            pass
                    if mtype in ['video', 'audio', 'photo']:
                        file_path = await bot.getFile(file_id)
                        file_url = 'https://api.telegram.org/file/bot' + key['telegram'] + '/' + file_path['file_path']
                        try:
                            ext = '.' + file_url.split('.')[3]
                        except IndexError:
                            ext = ''
                        if mtype == 'audio':
                            ext = '.ogg'
                        namevar = datetime.datetime.now().strftime("%Y%m%d%H%M%f") + ext
                        memedex = { mem : { 'filename' : namevar, 'mtype' : mtype, 'cap' : caption } }
                        memefeed['files'].update(memedex)
                        async with aiohttp.ClientSession() as session:
                            async with session.get(file_url) as r:
                                if r.status == 200:
                                    async with aiofiles.open(memedir + namevar, 'wb') as f:
                                        while True:
                                            chunk = await r.content.read(128)
                                            if not chunk:
                                                break
                                            await f.write(chunk)
                                else:
                                    await bot.sendMessage(chat_id, 'Telegram is messing up, I can\'t do anything about it sorry', reply_to_message_id=msg_id)
                                    return
                    elif mtype == 'quote':
                        memedex = { mem : { 'text' : quotetext, 'author' : authname } }
                        memefeed['quotes'].update(memedex)
                    with open(memeindex, 'w') as f:
                        json.dump(memefeed, f, indent=2)
                    await bot.sendMessage(chat_id, 'Meme stored, meme with `/meme ' + mem + '`', parse_mode='Markdown', reply_to_message_id=msg_id)
                    if mtype == 'video':
                        filefixer.mp4thumb()
                    elif mtype == 'audio':
                        filefixer.oggconv()
                    return
            except UnboundLocalError:
                return
        elif command.startswith('/meme'):
            try:
                mem = command.split(' ', 1)[1]
            except IndexError:
                return
            async with aiofiles.open(memeindex) as f:
                memefeed = json.loads(await f.read())
            try:
                memekey = memefeed['files'][mem]
            except KeyError:
                try:
                    memekey = memefeed['quotes'][mem]
                except KeyError:
                        await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
                        return
            await bot.sendChatAction(chat_id, 'typing')
            try:
                memtype = memekey['mtype']
            except KeyError:
                pass
            try:
                if memtype in  ['video', 'audio', 'photo']:
                    try:
                        async with aiofiles.open(memedir + memekey['filename'], 'rb') as m:
                            meme = await m.read()
                    except:
                        bot.sendMessage(chat_id, 'Something went wrong :(', reply_to_message_id=msg_id)
                    try:
                        capvar = memekey['cap']
                    except KeyError:
                        capvar = ''
                if memtype == 'audio':
                    await bot.sendVoice(chat_id, meme, reply_to_message_id=reply_id)
                elif memtype == 'video':
                    await bot.sendVideo(chat_id, meme, reply_to_message_id=reply_id, caption=capvar)
                elif memtype == 'photo':
                    await bot.sendPhoto(chat_id, meme, reply_to_message_id=reply_id, caption=capvar)
                else:
                    await bot.sendMessage(chat_id, 'Something went wrong :(', reply_to_message_id=msg_id)
            except UnboundLocalError:
               await bot.sendMessage(chat_id, memekey['text'] + '\n  <i>— ' + memekey['author'] + '</i>', reply_to_message_id=reply_id, parse_mode='html')
        elif command.startswith('/list'):
            if chat_type != 'private':
                await bot.sendMessage(chat_id, 'Ask in PM pls', reply_to_message_id=msg_id)
            else:
                async with aiofiles.open(memeindex) as f:
                    memefeed = json.loads(await f.read())
                temp = list()
                for k in memefeed.keys():
                    temp.append(list(memefeed[k]))
                temp = temp[0] + temp[1]
                memlist = list()
                for i in temp:
                    formatt = '- ' + i + '\n'
                    memlist.append(formatt)
                memelist = ''.join(memlist)
                await bot.sendMessage(chat_id, memelist, parse_mode='html')
        elif command.startswith('/delet'):
            if from_id == 105301944:
                try:
                    mem = command.split(' ', 1)[1]
                except IndexError:
                    return
                async with aiofiles.open(memeindex) as f:
                    memefeed = json.loads(await f.read())
                try:
                    memekey = memefeed['files'][mem]
                except KeyError:
                    try:
                        memekey = memefeed['quotes'][mem]
                    except KeyError:
                        await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
                        return
                try:
                    memef = memedir + memekey['filename']
                    os.remove(memef)
                    del memefeed['files'][mem]
                except KeyError:
                    del memefeed['quotes'][mem]
                with open(memeindex, 'w') as f:
                    json.dump(memefeed, f, indent=2)
                await bot.sendMessage(chat_id, 'Meme baleet >:U', reply_to_message_id=msg_id)
    else:
        return

def on_inline_query(msg):
    query_id, from_id, query_string, offset = telepot.glance(msg, flavor='inline_query', long=True)
    #print(msg)
    memeslist = []
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    qstring = query_string.lower()
    #texd = await quote_getter(qstring)
    #print(texd)
    next_offset = int(offset) if offset != '' else 0
    def compute():
        offset = next_offset
        mlist = meme_getter(qstring)
        #print(mlist)
        rnint = random.sample(range(5000), 50)
        for i, n in zip(mlist, rnint):
            for key, value in i.items():
                memetitle = key
                memetype = value['mtype']
                memename = value['filename']
                try:
                    memecap = value['cap']
                except KeyError:
                    memecap = ''
                if memetype == 'photo':
                    memeslist.append(InlineQueryResultPhoto(
                        id=str(n),
                        title=memetitle,
                        photo_url=baseurl + 'memes/' + memename,
                        thumb_url=baseurl + 'memes/' + memename,
                        caption=memecap
                        ))
                elif memetype == 'video':
                    memeslist.append(InlineQueryResultVideo(
                        id=str(n),
                        title=memetitle,
                        video_url=baseurl + 'memes/' + memename,
                        mime_type='video/mp4',
                        thumb_url=baseurl + 'memes/t_' + memename + '.jpg',
                        caption=memecap
                        ))
                elif memetype == 'audio':
                    memeslist.append(InlineQueryResultAudio(
                        id=str(n),
                        audio_url=baseurl + 'memes/' + memename,
                        title=memetitle,
                        caption=memecap
                        ))
                else:
                    return
        qlist = quote_getter(qstring)[offset:-1]
        rnint = random.sample(range(5000), 50)
        if len(qlist[offset:]) > 50:
            qlist = qlist[offset:offset + 50]
            offset=str(int(offset) + 51 )
        else:
            qlist = qlist[:50]
            offset = ''
        for i, n in zip(qlist, rnint):
                for key, value in i.items():
                    memetitle = key
                    memetext = value['text']
                    memeauthor = value['author']
                    memeslist.append(InlineQueryResultArticle(
                        id=str(n), title=memetitle,
                        input_message_content=InputTextMessageContent(
                            message_text=memetext + '\n <i>— ' + memeauthor + '</i>',
                            parse_mode='html')
            ))
                #print(memeslist)
        return { 'results' : memeslist, 'cache_time' : 30, 'next_offset' : offset }
    if len(qstring) > 0:
        answerer.answer(msg, compute)
    else:
        return
def quote_getter(qname):
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    qlist = memefeed['quotes']
    memelobj = []
    for i in list(qlist.keys()):
        if regex.search(qname, i):
            memedict = {
                    i: {
                        'text': qlist[i]['text'],
                        'author' : qlist[i]['author'],
                    }
                }
            memelobj.append(memedict)
    return memelobj

def meme_getter(mname):
    memelobj = []
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    mlist = memefeed['files']
    for i in list(mlist.keys()):
        if regex.search(mname, i):
            keys = [i]
            mdict = {x:mlist[x] for x in keys}
            memelobj.append(mdict)
    return memelobj

async def storem(mname):
    return

async def chosen_return(msg):
    return
    
answerer = telepot.aio.helper.Answerer(bot)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot,{'chat' : on_command,
                                   'inline_query' : on_inline_query,
                                   'chosen_inline_result' : chosen_return}).run_forever())
print('Started...')
loop.run_forever()