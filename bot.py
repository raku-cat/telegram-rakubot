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
import getter
from threading import Lock
import requests
import commands
import utils
import settings

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
bot = telepot.aio.Bot(key['telegram'])
memedir = sys.path[0] + '/memes/'
memeindex = 'memeindex.json'
if not os.path.exists(memeindex):
    with open(memeindex, 'w') as f:
        json.dump({'files' : {}, 'quotes' : {}}, f)
lock = Lock()

async def on_command(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    try:
        botcom = msg['entities'][0]['type']
        if not botcom == 'bot_command':
            return
    except KeyError:
        return
    if content_type == 'text':
        raw_message, command, command_argument, msg_reply, command_from = utils.Parser(msg)
        try:
            reply_id = msg_reply['message_id']
        except TypeError:
            reply_id = 'None'
        if command_argument is not None:
            if regex.search(r'\/store(\@raku_bot)?\Z', command) is not None:
                if msg_reply is not None:
                    await bot.sendChatAction(chat_id, 'typing')
                    if not utils.Exists(command_argument) and not utils.legacyExists(command_argument):
                        s = commands.Handler(msg_reply)
                        if s.store(command_argument, command_from):
                            await bot.sendMessage(chat_id, 'Meme stored, meme with `/meme ' + command_argument + '`', parse_mode='Markdown', reply_to_message_id=msg_id)
                        else:
                            await bot.sendMessage(chat_id, 'Something went wrong :\'(', reply_to_message_id=msg_id)
                    else:
                        await bot.sendMessage(chat_id, 'Mem already exist :V', reply_to_message_id=msg_id)
            if regex.search(r'\/meme(\@raku_bot)?\Z', command) is not None:
                await bot.sendChatAction(chat_id, 'typing')
                if utils.Exists(command_argument):
                    s = commands.Handler(msg)
                    sendwith, gotmeme, memekw = s.send(command_argument)
                    await getattr(bot, sendwith)(chat_id, *gotmeme, **memekw, reply_to_message_id=reply_id)
                #elif utils.legacyExists(command_argument):
                #    s = commands.Handler(msg)
                #    sendwith, gotmeme, memekw = s.send(command_argument)
                #    await getattr(bot, sendwith)(chat_id, *gotmeme, **memekw, reply_to_message_id=reply_id)
                else:
                    await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
        elif command.startswith('/list') or command.startswith('/start@raku_bot'):
            await bot.sendChatAction(chat_id, 'typing')
            await lister(msg)
        elif command.startswith('/delet'):
            if from_id == 105301944:
                await bot.sendChatAction(chat_id, 'typing')
                await deleter(msg)
            else:
                return
        elif command.startswith('/sauce'):
            await bot.sendChatAction(chat_id, 'typing')
            await meme_sauce(msg)
        elif command.startswith('/pray'):
            await bot.sendChatAction(chat_id, 'typing')
            await prayer(msg)
        elif command.startswith('/lucc'):
            await bot.sendChatAction(chat_id, 'typing')
            await lucc(msg)
        elif content_type == 'voice':
            print('beep')
    else:
        return

async def store_meme(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    try:
        reply = msg['reply_to_message']
        reply_id = reply['message_id']
    except KeyError:
        reply_id = 'None'
    command = msg['text'].lower()
    #print(reply)
    try:
        mem = command.split(' ', 1)[1]
    except IndexError:
        await bot.sendMessage(chat_id, 'Expected second argument as name `/store <name>`', parse_mode='Markdown')
        return
    if reply_id is not None:
        typeaud = reply.get('audio', {}).get('file_id')
        typepic = reply.get('photo')
        typedoc = reply.get('document', {}).get('file_id')
        typevid = reply.get('video', {}).get('file_id')
        typechat = reply.get('text')
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
    elif typevid is not None:
        mtype='video'
        file_id = typevid
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
    try:
        sauce = msg['from']['username']
    except KeyError:
        sauce = ''
    if mtype in ['video', 'audio', 'photo']:
        try:
            caption
        except UnboundLocalError:
            caption = ''
        memedex = { mem : { 'file_id' : file_id, 'mtype' : mtype, 'cap' : caption, 'sauce' : sauce } }
        memefeed['files'].update(memedex)
#        async with aiohttp.ClientSession() as session:
#            async with session.get(file_url) as r:
#                if r.status == 200:
#                    async with aiofiles.open(memedir + namevar, 'wb') as f:
#                        while True:
#                            chunk = await r.content.read(128)
#                            if not chunk:
#                                break
#                            await f.write(chunk)
#                else:
#                    await bot.sendMessage(chat_id, 'Telegram is messing up, I can\'t do anything about it sorry', reply_to_message_id=msg_id)
#                    return
    elif mtype == 'quote':
        memedex = { mem : { 'text' : quotetext, 'author' : authname, 'sauce' : sauce } }
        memefeed['quotes'].update(memedex)
    with lock:
        with open(memeindex, 'w') as f:
            json.dump(memefeed, f, indent=2)
    await bot.sendMessage(chat_id, 'Meme stored, meme with `/meme ' + mem + '`', parse_mode='Markdown', reply_to_message_id=msg_id)
    if mtype == 'video':
        filefixer.mp4thumb()
    elif mtype == 'audio':
        filefixer.oggconv()

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
        meme = memekey['file_id']
    except KeyError:
        try:
            legacykey = getter.legacyfile(mem)[mem]
        except KeyError:
            try:
                memekey = getter.quotes(mem)[mem]
            except KeyError:
                await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
                return
    try:
        memtype = memekey['mtype']
    except UnboundLocalError:
        try:
            memtype = legacykey['mtype']
        except KeyError:
            pass
    except KeyError:
        pass
    try:
        if memtype in  ['video', 'audio', 'photo']:
            try:
                async with aiofiles.open(memedir + legacykey['filename'], 'rb') as m:
                    legacymeme = await m.read()
            except:
                pass 
            try:
                capvar = memekey['cap']
            except UnboundLocalError:
                try:
                    capvar = legacykey['cap']
                except KeyError:
                    capvar = ''
        if memtype == 'audio':
            try:
                await bot.sendVoice(chat_id, meme, reply_to_message_id=reply_id, caption=capvar)
            except UnboundLocalError:
                oldmeme = await bot.sendVoice(chat_id, legacymeme, reply_to_message_id=reply_id)
                newid = oldmeme.get('audio', {}).get('file_id')
                try:
                    oldsauce = legacykey['sauce']
                except KeyError:
                    oldsauce = ''
                memedex = { mem : { 'file_id' : newid, 'mtype' : memtype, 'cap' : capvar, 'sauce' : oldsauce } }
                async with aiofiles.open(memeindex) as f:
                    memefeed = json.loads(await f.read())
                memefeed['files'].update(memedex)
                with lock:
                    with open(memeindex, 'w') as f:
                        json.dump(memefeed, f, indent=2)
                os.remove(memedir + legacykey['filename'])
        elif memtype == 'video':
            try:
                await bot.sendDocument(chat_id, meme, reply_to_message_id=reply_id, caption=capvar)
            except UnboundLocalError:
                oldmeme = await bot.sendVideo(chat_id, legacymeme, reply_to_message_id=reply_id, caption=capvar)
                print(oldmeme)
                newid = oldmeme.get('video', {}).get('file_id')
                if newid is None:
                    newid = oldmeme.get('document', {}).get('file_id')
                try:
                    oldsauce = legacykey['sauce']
                except KeyError:
                    oldsauce = ''
                memedex = { mem : { 'file_id' : newid, 'mtype' : memtype, 'cap' : capvar, 'sauce' : oldsauce } }
                async with aiofiles.open(memeindex) as f:
                    memefeed = json.loads(await f.read())
                memefeed['files'].update(memedex)
                with lock:
                    with open(memeindex, 'w') as f:
                        json.dump(memefeed, f, indent=2)
                os.remove(memedir + legacykey['filename']);
        elif memtype == 'photo':
            try:
                await bot.sendPhoto(chat_id, meme, reply_to_message_id=reply_id, caption=capvar)
            except UnboundLocalError:
                oldmeme = await bot.sendPhoto(chat_id, legacymeme, reply_to_message_id=reply_id, caption=capvar)
                newphoto = oldmeme.get('photo')
                newid = newphoto[-1]['file_id']
                try:
                    oldsauce = legacykey['sauce']
                except KeyError:
                    oldsauce = ''
                memedex = { mem : { 'file_id' : newid, 'mtype' : memtype, 'cap' : capvar, 'sauce' : oldsauce } }
                async with aiofiles.open(memeindex) as f:
                    memefeed = json.loads(await f.read())
                memefeed['files'].update(memedex)
                with lock:
                    with open(memeindex, 'w') as f:
                        json.dump(memefeed, f, indent=2)
                os.remove(memedir + legacykey['filename']);
        else:
            await bot.sendMessage(chat_id, 'Something went wrong :(', reply_to_message_id=msg_id)
    except UnboundLocalError:
       await bot.sendMessage(chat_id, memekey['text'] + '\n  <i>— ' + memekey['author'] + '</i>', reply_to_message_id=reply_id, parse_mode='html')

async def lister(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    #print(msg)
    if chat_type != 'private':
        if msg['text'].lower() == '/list' or '/list@rakubot':
            await bot.sendMessage(chat_id, '<a href="http://telegram.me/raku_bot?start=list">Ask in PM pls</a>', reply_to_message_id=msg_id, parse_mode='html', disable_web_page_preview=True)
        else:
            return
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

async def meme_sauce(msg):
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
        await bot.sendMessage(chat_id, 'this was @' + memekey['sauce'] + ' tbh.......', reply_to_message_id=msg_id)
    except KeyError:
        return

async def lucc(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    try:
        reply = msg['reply_to_message']
        reply_id = reply['message_id']
    except KeyError:
        reply_id = 'None'
    with open(memeindex) as f:
        memefeeds = json.load(f)
    memf = memefeeds[random.choice(list(memefeeds.keys()))]
    luckymeme =  memf[random.choice(list(memf.keys()))]
    try:
        memtype = luckymeme['mtype']
    except KeyError:
        pass
    try:
        if memtype in  ['video', 'audio', 'photo']:
            try:
                async with aiofiles.open(memedir + luckymeme['filename'], 'rb') as m:
                    meme = await m.read()
            except:
                bot.sendMessage(chat_id, 'Something went wrong :(', reply_to_message_id=msg_id)
            try:
                capvar = luckymeme['cap']
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
        await bot.sendMessage(chat_id, luckymeme['text'] + '\n  <i>— ' + luckymeme['author'] + '</i>', reply_to_message_id=reply_id, parse_mode='html')

async def prayer(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    command = msg['text'].lower()
    try:
        mem = command.split(' ', 1)[1]
    except IndexError:
        return
    prayer = "".join(mem.split())
    await bot.sendMessage(chat_id, 'In light of recent events, we\'d like to #prayfor' + prayer)

def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    #print(msg)
    memeslist = []
    with open(memeindex) as f:
        memefeed = json.loads(f.read())
    qstring = query_string.lower()
    api_key = key['telegram']
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
                file_id = value['file_id']
                file_path = requests.get('https://api.telegram.org/bot' + api_key + '/getFile?file_id=' + file_id).json()['result']['file_path']
                file_url = 'https://api.telegram.org/file/bot' + api_key + '/' + file_path
                try:
                    memecap = value['cap']
                except KeyError:
                    memecap = ''
                if memetype == 'photo':
                    memeslist.append(InlineQueryResultPhoto(
                        id=str(n),
                        title=memetitle,
                        photo_url=file_url,
                        thumb_url=file_url,
                        caption=memecap
                        ))
                elif memetype == 'video':
                    memeslist.append(InlineQueryResultVideo(
                        id=str(n),
                        title=memetitle,
                        video_url=file_url,
                        mime_type='video/mp4',
                        thumb_url=file_url,
                        caption=memecap
                        ))
                elif memetype == 'audio':
                    memeslist.append(InlineQueryResultVoice(
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
