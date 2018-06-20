#!/usr/bin/env python3
import settings
import json
import os
import regex
import telepot, telepot.aio
import asyncio, aiofiles, aiohttp
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.aio.loop import MessageLoop
import commands.deleter
import commands.lister
import commands.lucc
import commands
import utils
import inline

key = settings.getKeys()
memeindex = settings.PROJECT_ROOT + '/memeindex.json'
legacy_memeindex = settings.PROJECT_ROOT + '/memes/memeindex.json'
memedir = settings.PROJECT_ROOT + '/memes/'
bot = telepot.aio.Bot(key['telegram'])

if not os.path.exists(memeindex):
    with open(memeindex, 'w') as f:
        json.dump({'files' : {}, 'quotes' : {}}, f)

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
        if regex.search(r'\/store(\@raku_bot)?\Z', command) is not None:
            if msg_reply is not None:
                await bot.sendChatAction(chat_id, 'typing')
                if not await utils.Exists(command_argument):
                    s = commands.Handler(msg_reply)
                    if await s.store(command_argument, command_from):
                        await bot.sendMessage(chat_id, 'Meme stored, meme with `/meme ' + command_argument + '`', parse_mode='Markdown', reply_to_message_id=msg_id)
                    else:
                        await bot.sendMessage(chat_id, 'Something went wrong :\'(', reply_to_message_id=msg_id)
                else:
                    await bot.sendMessage(chat_id, 'Mem already exist :V', reply_to_message_id=msg_id)
        if regex.search(r'\/meme(\@raku_bot)?\Z', command) is not None:
            if command_argument is not None:
                await bot.sendChatAction(chat_id, 'typing')
                if await utils.Exists(command_argument):
                    s = commands.Handler(msg)
                    sendwith, gotmeme, memekw = await s.send(command_argument)
                    await getattr(bot, sendwith)(chat_id, *gotmeme, **memekw, reply_to_message_id=reply_id)
                else:
                    await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
        elif regex.search(r'\/list(\@raku_bot)?\Z', command) is not None or regex.search(r'\/start(\@raku_bot)?\Z', command) is not None and command_argument == 'list':
            await bot.sendChatAction(chat_id, 'typing')
            if utils.isPrivate(msg):
                await bot.sendMessage(chat_id, await commands.lister.getList(), parse_mode='html')
            else:
                await bot.sendMessage(chat_id, '<a href="http://telegram.me/raku_bot?start=list">Ask in PM pls</a>', reply_to_message_id=msg_id, parse_mode='html', disable_web_page_preview=True)
        elif regex.search(r'\/sauce(\@raku_bot)?\Z', command) is not None:
            if msg_reply is not None or command_argument is not None:
                await bot.sendChatAction(chat_id, 'typing')
            if msg_reply is None:
                if command_argument is not None:
                    if await utils.Exists(command_argument):
                        s = commands.Handler(msg)
                        author = await s.sauce(command_argument)
                    else:
                        await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
                else:
                    return
            elif msg_reply is not None:
                s = commands.Handler(msg_reply)
                author = await s.sauce()
            try:
                if author:
                    await bot.sendMessage(chat_id, 'this was @' + author + ' tbh.......', reply_to_message_id=msg_id)
                else:
                    await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
            except UnboundLocalError:
                return
        elif regex.search(r'\/lucc(\@raku_bot)?\Z', command) is not None:
            await bot.sendChatAction(chat_id, 'typing')
            luckymeme = await commands.lucc.getLucc()
            s = commands.Handler(msg)
            sendwith, gotmeme, memekw = await s.send(luckymeme)
            await getattr(bot, sendwith)(chat_id, *gotmeme, **memekw, reply_to_message_id=reply_id)
        elif regex.search(r'\/pray(\@raku_bot)?\Z', command) is not None:
            await bot.sendChatAction(chat_id, 'typing')
            await bot.sendMessage(chat_id, 'In light of recent events, we\'d like to #prayfor' + command_argument)
        elif regex.search(r'\/delet(\@raku_bot)?\Z', command) is not None:
            from_id = msg['from']['id']
            if from_id == 105301944:
                if command_argument is not None:
                    await bot.sendChatAction(chat_id, 'typing')
                    if await utils.Exists(command_argument):
                        if await commands.deleter.deleteMeme(command_argument):
                            await bot.sendMessage(chat_id, 'Meme baleet >:U', reply_to_message_id=msg_id)
                    else:
                        await bot.sendMessage(chat_id, 'Meme not found', reply_to_message_id=msg_id)
            else:
                return
    else:
        return

async def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    inlineObj = inline.Inline(msg)
    answerer.answer(msg, inlineObj.result)

answerer = telepot.aio.helper.Answerer(bot)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot,{'chat' : on_command,
                                   'inline_query' : on_inline_query}).run_forever())
print('Started...')
loop.run_forever()
