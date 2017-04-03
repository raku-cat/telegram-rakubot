#!/usr/bin/env python3
import sys
import telepot
import json
import requests
import os
import glob
from pprint import pprint

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
bot = telepot.Bot(key['telegram'])

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
            pass
        command = msg['text'].lower()
        if command.startswith('/meme'):
            try:
                mem = command.split(' ')[1]
                if mem == 'store':
                    if is_reply:
                        pprint(is_reply, width=1)
                        try:
                            is_reply['audio']
                            print('audio')
                        except KeyError:
                            try:
                                is_reply['photo']
                                print('picture')
                            except KeyError:
                                try:
                                    doc = is_reply['document']['mime_type'].split('/')[0]
                                    if doc == 'video':
                                        print('video')
                                    elif doc == 'audio':
                                        print('audio')
                                except KeyError:
                                    try:
                                        is_reply['chat']
                                        print('chat')
                                    except KeyError:
                                        bot.sendMessage(chat_id, 'Idk what that is, i can\'t grab it')
                else:
                #print(mem)
                    try:
                        meme = sys.path[0] + '/memes/'+ mem + '.flac'
                        meme = open(meme, 'rb')
                        bot.sendChatAction(chat_id, 'upload_audio')
                        bot.sendAudio(chat_id, meme, reply_to_message_id=reply_id)
                    except FileNotFoundError:
                        bot.sendMessage(chat_id, 'Meme not found')
            except IndexError:
                return
        else:
            return

bot.message_loop(handler, run_forever='Started...')