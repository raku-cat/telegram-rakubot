#!/usr/bin/env python3
import sys
import telepot, telepot.aio
import asyncio, aiofiles, aiohttp
import json
import datetime
import os

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
bot = telepot.aio.Bot(key['telegram'])
loop = asyncio.get_event_loop()
memedir = sys.path[0] + '/memes/'
if not os.path.exists(memedir):
    os.makedirs(memdir)
memeindex = memedir + 'memeindex.json'
if not os.path.exists(memeindex):
    with open(memeindex, 'w') as f:
        json.dump({'files' : {}, 'quotes' : {'mtype' : 'quote'} }, f)


async def handler(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    #print(chat_type, content_type, chat_id)
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
            try:
                if reply:
                    try:
                        file_id = reply['audio']['file_id']
                        mtype = 'audio'
                    except KeyError:
                        try:
                            file_id = reply['photo'][-1]['file_id']
                            mtype = 'photo'
                        except KeyError:
                            try:
                                file_id = reply['document']['file_id']
                                dmtye = reply['document']['mime_type'].split('/')[0]
                                if dmtye == 'audio':
                                    mtype = 'audio'
                                elif dmtye == 'video':
                                    mtype = 'video'
                            except KeyError:
                                try:
                                    reply['chat']
                                    authname = '@' + reply['from']['username']
                                    quotetext = reply['text']
                                    mtype = 'quote'
                                except KeyError:
                                    await bot.sendMessage(chat_id, 'Idk what that is, i can\'t grab it')
                    async with aiofiles.open(memeindex) as f:
                        memefeed = json.loads(await f.read())
                    try:
                        memefeed['files'][mem]
                        await bot.sendMessage(chat_id, 'Mem already exist :V', reply_to_message_id=msg_id)
                    except KeyError:
                        try:
                            memefeed['quotes'][mem]
                            await bot.sendMessage(chat_id, 'Mem already exist :V', reply_to_message_id=msg_id)
                        except KeyError:
                            pass
                    if mtype in ['video', 'audio', 'photo']:
                        file_path = await bot.getFile(file_id)
                        file_url = 'https://api.telegram.org/file/bot' + key['telegram'] + '/' + file_path['file_path']
                        ext = file_url.split('.')[3]
                        ext = '.' + ext
                        namevar = datetime.datetime.now().strftime("%Y%m%d%H%M%f") + ext
                        memedex = { mem : { 'filename' : namevar, 'mtype' : mtype } }
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
                    elif mtype == 'quote':
                        memedex = { mem : { 'text' : quotetext, 'author' : authname } }
                        memefeed['quotes'].update(memedex)
                    with open(memeindex, 'w') as f:
                        json.dump(memefeed, f, indent=2)
                    await bot.sendMessage(chat_id, 'Meme stored, meme with `/meme ' + mem + '`', parse_mode='Markdown', reply_to_message_id=msg_id)
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
                if memtype == 'audio':
                    await bot.sendVoice(chat_id, meme, reply_to_message_id=reply_id)
                elif memtype == 'video':
                    await bot.sendVideo(chat_id, meme, reply_to_message_id=reply_id)
                elif memtype == 'photo':
                    await bot.sendPhoto(chat_id, meme, reply_to_message_id=reply_id)
                else:
                    await bot.sendMessage(chat_id, 'Something went wrong :(', reply_to_message_id=msg_id)
            except UnboundLocalError:
               await bot.sendMessage(chat_id, memekey['text'] + '\n  <i>-' + memekey['author'] + '</i>', reply_to_message_id=reply_id, parse_mode='html')
        elif command.startswith('/list'):
            if chat_type != 'private':
                await bot.sendMessage(chat_id, 'Ask in PM pls', reply_to_message_id=msg_id)
            else:
                async with aiofiles.open(memeindex) as f:
                    memefeed = json.loads(await f.read())
                temp = list()
                for key in memefeed.keys():
                    temp.append(list(memefeed[key]))
                temp = temp[0] + temp[1]
                memlist = list()
                for i in temp:
                    formatt = '- ' + i + '\n'
                    memlist.append(formatt)
                memelist = ''.join(memlist)
                #memelist = ', '.join(memelist).replace('\\\\', '\\')
                await bot.sendMessage(chat_id, memelist, parse_mode='html')
    else:
        return

loop.create_task(bot.message_loop(handler))
print('Started...')
loop.run_forever()