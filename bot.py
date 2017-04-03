#!/usr/bin/env python3
import sys
import telepot
import json
import requests
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
memejson = memedir + '/memes.json'
if not os.path.exists(memejson):
    open(memejson, 'w')


def handler(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    #print(chat_type, content_type, chat_id)
    if content_type != 'text':
        return
    else:
        try:
            is_reply = msg['reply_to_message']
            reply_id = is_reply['message_id']
        except KeyError:
            reply_id = 'None'
        command = msg['text'].lower()
        if command.startswith('/meme'):
            try:
                mem = command.split(' ')[1]
                if mem == 'store':
                    try:
                        memname = command.split(' ')[2]
                    except IndexError:
                        bot.sendMessage(chat_id, 'Expected third argument as name `/meme store <name>`', parse_mode='Markdown')
                        return
                    if is_reply:
#                        pprint(is_reply, width=1)
                        try:
                            file_id = is_reply['audio']['file_id']
                            print('audio')
                        except KeyError:
                            try:
                                file_id = is_reply['photo'][-1]['file_id']
                                print('picture')
                            except KeyError:
                                try:
                                    file_id = is_reply['document']['file_id']
#                                    if doc == 'video':
#                                        print('video')
#                                    elif doc == 'audio':
#                                        print('audio')
                                except KeyError:
                                    try:
                                        is_reply['chat']
                                        print('chat')
                                    except KeyError:
                                        bot.sendMessage(chat_id, 'Idk what that is, i can\'t grab it')
                    file_url = 'https://api.telegram.org/file/bot' + key['telegram'] + '/' + bot.getFile(file_id)['file_path']
                    #print(file_url)
                    ext = file_url.split('.')[3]
                    response = requests.get(file_url, stream=True)
                    with open(memedir + memname + '.' + ext, 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                    del response
                    bot.sendMessage(chat_id, 'Meme stored, send with `/meme ' + memname + '`', parse_mode='Markdown')
                else:
                #print(mem)
                    try:
                        for infile in glob.glob(os.path.join(memedir, mem + '.*')):
                            meme = open(infile, 'rb')
                        #print(meme)
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
                    except FileNotFoundError:
                        bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
            except IndexError:
                bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
        else:
            return

bot.message_loop(handler, run_forever='Started...')