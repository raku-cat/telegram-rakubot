import telepot

def Parser(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    from_id = msg['from']['id']
    try:
        reply = msg['reply_to_message']
    except KeyError:
        reply = 'None'
    raw = msg['text'].lower()
    print(raw)
    command = raw.split(' ', 1)[0]
    try:
        argument = raw.split(' ', 1)[1]
    except IndexError:
        return
#    print(command)
#    print(argument)
    c_from = msg['from']['username']
#    command_dict = { 'raw' : raw,
#                    'command' : command,
#                    'argument' : argument,
#                    'reply' : reply,
#                    'from': c_from
#                    }
    command_dict = [raw, command, argument, reply, c_from]
    return command_dict


