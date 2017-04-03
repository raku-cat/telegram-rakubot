#!/usr/bin/env python3
import sys
import telepot
import json
import requests
import datetime
import os
import glob
import magic
from pprint import pprint
import shutil

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
bot = telepot.Bot(key['telegram'])
memedir = sys.path[0] + '/memes/'
if not os.path.exists(memedir):
    os.makedirs(memdir)
memeindex = memedir + 'memeindex.json'
if not os.path.exists(memeindex):
    open(memeindex, 'wb')


def handler(msg):
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
            pprint(reply, width=1)
            bot.sendChatAction(chat_id, 'typing')
            try:
                mem = command.split(' ', 1)[1]
            except IndexError:
                bot.sendMessage(chat_id, 'Expected second argument as name `/store <name>`', parse_mode='Markdown')
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
                                except KeyError:
                                    bot.sendMessage(chat_id, 'Idk what that is, i can\'t grab it')
                    file_url = 'https://api.telegram.org/file/bot' + key['telegram'] + '/' + bot.getFile(file_id)['file_path']
                    #print(file_url)
                    ext = file_url.split('.')[3]
                    ext = '.' + ext
                    namevar = datetime.datetime.now().strftime("%Y%m%d%H%M%f") + ext
                    memedex = { 'files' : { mem : { 'filename' : namevar, 'mtype' : mtype } } }
                    print(memedex)
                    memeson = json.dumps(memedex, indent=4)
                    #print(memeson)
                    with open(memeindex) as f:
                        memefeed = json.load(f)
                    memefeed.update(memeson)
                    with open(memeindex, 'wb') as f:
                        json.dump(memefeed, f)
                    response = requests.get(file_url, stream=True)
                    with open(memedir + namevar + '.' + ext, 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                    del response
                    bot.sendMessage(chat_id, 'Meme stored, send with `/meme ' + mem + '`', parse_mode='Markdown', reply_to_message_id=msg_id)
            except UnboundLocalError:
                print('beep')
        elif command.startswith('/meme'):
            try:
                mem = command.split(' ', 1)[1]
            except IndexError:
                return
            try:
                for infile in glob.glob(os.path.join(memedir, mem + '.*')):
                    meme = open(infile, 'rb')
            except FileNotFoundError:
                bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
                return
            bot.sendChatAction(chat_id, 'typing')
            m = magic.open(magic.MAGIC_MIME)
            m.load()
            memtype = m.file(str(glob.glob(os.path.join(memedir, mem + '.*'))[0])).split('/')[0]
            m.close()
            #print(memtype)
            if memtype == 'audio':
                bot.sendAudio(chat_id, meme, reply_to_message_id=reply_id)
            elif memtype == 'video':
                bot.sendVideo(chat_id, meme, reply_to_message_id=reply_id)
            elif memtype == 'image':
                bot.sendPhoto(chat_id, meme, reply_to_message_id=reply_id)
            else:
                bot.sendMessage(chat_id, 'Something went wrong :(', reply_to_message_id=msg_id)
                return
        else:
            return
    else:
        return

bot.message_loop(handler, run_forever='Started...')