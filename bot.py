#!/usr/bin/env python3
import sys
import telepot, telepot.aio
import asyncio, aiofiles, aiohttp
import json
import datetime
import os
import random
import markovify
import regex
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, InlineQueryResultVideo, InlineQueryResultVoice, InlineQueryResultGif, InlineQueryResultMpeg4Gif, InlineQueryResultAudio
import filefixer
import getter

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
            await store_meme(msg)
        elif command.startswith('/meme'):
            await bot.sendChatAction(chat_id, 'typing')
            await meme_sender(msg)
        elif command.startswith('/list') or command.startswith('/start'):
            await bot.sendChatAction(chat_id, 'typing')
            await lister(msg)
        elif command.startswith('/delet'):
            if from_id == 105301944:
                await bot.sendChatAction(chat_id, 'typing')
                await deleter(msg)
            else:
                return
        elif random.uniform(0.0, 1.0) < 0.01 or 'tf' in command or 'blort' in command:
            luzylist = []
            async with aiofiles.open(memeindex) as f:
                luzyindex = json.loads(await f.read())
            for key, value in luzyindex['quotes'].items():
                if value['author'] == '@luzy_lu' or 'luzy' in key:
                    luzylist.append(value['text'])
            luzystrings = '\n'.join(luzylist)
            luzy_model = markovify.NewlineText(luzystrings, state_size=1)
            luzy_message = luzy_model.make_short_sentence(140)
            if luzy_message is not None:
                await bot.sendMessage(chat_id, luzy_message)

async def store_meme(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    try:
        reply = msg['reply_to_message']
        reply_id = reply['message_id']
    except KeyError:
        reply_id = 'None'
    command = msg['text'].lower()
    try:
        mem = command.split(' ', 1)[1]
    except IndexError:
        await bot.sendMessage(chat_id, 'Expected second argument as name `/store <name>`', parse_mode='Markdown')
        return
    if reply_id is not None:
        typeaud = reply.get('audio', {}).get('file_id')
        typepic = reply.get('photo')
        typedoc = reply.get('document', {}).get('file_id')
        typechat = reply.get('chat')
        typevoice = reply.get('voice', {}).get('file_id')
    if typeaud is not None:
        mtype = 'audio'
        file_id = typeaud
    elif typepic is not None:
        mtype = 'photo'
        file_id = typepic[-1]['file_id']
        try:
            caption = reply['caption']
        except KeyError:
            caption = ''
    elif typedoc is not None:
        file_id = typedoc
        dmtye = reply['document']['mime_type'].split('/')[0]
        if dmtye == 'audio':
            mtype = 'audio'
        elif dmtye == 'video':
            mtype = 'video'
            try:
                caption = reply['caption']
            except KeyError:
                caption = ''
    elif typechat is not None:
        try:
            authname = '@' + reply['forward_from']['username']
        except KeyError:
            authname = '@' + reply['from']['username']
        quotetext = reply['text']
        mtype = 'quote'
    elif typevoice is not None:
        mtype = 'audio'
        file_id = typevoice
    else:
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

async def meme_sender(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    command = msg['text'].lower()
    try:
        reply = msg['reply_to_message']
        reply_id = reply['message_id']
    except KeyError:
        reply_id = 'None'

    try:
        mem = command.split(' ', 1)[1]
    except IndexError:
        return
    try:
        memekey = getter.files(mem)[mem]
    except KeyError:
        try:
            memekey = getter.quotes(mem)[mem]
        except KeyError:
                await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
                return
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

async def lister(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    #print(msg)
    if chat_type != 'private':
        await bot.sendMessage(chat_id, '<a href="http://telegram.me/raku_bot?start=list">Ask in PM pls</a>', reply_to_message_id=msg_id, parse_mode='html', disable_web_page_preview=True)
    else:
        if msg['text'].lower().startswith('/start'):
            if msg['text'].split(' ')[1] == 'list':
                pass
            else:
                return
        else:
            pass
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

async def deleter(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    command = msg['text'].lower()
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

def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    #print(msg)
    memeslist = []
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    qstring = query_string.lower()
    def compute():
        memelobj = []
        quotelobj = []
        mlist = memefeed['files']
        qlist = memefeed['quotes']
        for i in list(mlist.keys()):
            if regex.search(qstring, i):
                memelobj.append(getter.files(i))
                #print(memelobj)
        for i in list(qlist.keys()):
            if regex.search(qstring, i):
                quotelobj.append(getter.quotes(i))
        rnint = random.sample(range(5000), 50)
        for d, n in zip(memelobj, rnint):
            for key, value in d.items():
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
        rnint = random.sample(range(5000), 50)
        for q, n in zip(quotelobj, rnint):
                for key, value in q.items():
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
        if len(memeslist) > 50:
            memeslistfinal = memeslist[:50]
        else:
            memeslistfinal = memeslist
        return { 'results' : memeslistfinal, 'cache_time' : 30 }
    answerer.answer(msg, compute)

answerer = telepot.aio.helper.Answerer(bot)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot,{'chat' : on_command,
                                   'inline_query' : on_inline_query}).run_forever())
print('Started...')
loop.run_forever()
