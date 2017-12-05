import telepot
import commands.store

class Handler:

    def __init__(self, msg):
        self.content_type, self.chat_type, self.chat_id, self.msg_date, self.msg_id = telepot.glance(msg, long=True)
        self.msg = msg

    def store(self, mtitle, sauce):
        parsed_meme = commands.store.parse(self.msg, self.content_type)
        parsed_meme['sauce'] = sauce
        memedict = { mtitle : parsed_meme }
#        print(memedict)
        if self.content_type in ('voice','video','document','audio','photo'): 
            return commands.store.insert_file(memedict)
        elif self.content_type == 'text':
            return commands.store.insert_quote(memedict)

