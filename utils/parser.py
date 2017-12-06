import telepot

def Parser(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    try:
        reply = msg['reply_to_message']
    except KeyError:
        reply = 'None'
    raw = msg['text'].lower()
    command = raw.split(' ', 1)[0]
    try:
        argument = raw.split(' ', 1)[1]
    except IndexError:
        argument = 'None'
    c_from = msg['from']['username']
    parsed_command_tuple = [raw, command, argument, reply, c_from]
    return parsed_command_tuple


