import telepot

def isPrivate(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    if chat_type == 'private':
        return True
    else:
        return False
