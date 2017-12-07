import telepot
import commands.store
import commands.send

class Handler:

    def __init__(self, msg):
        self.content_type, self.chat_type, self.chat_id, self.msg_date, self.msg_id = telepot.glance(msg, long=True)
        self.msg = msg

    def store(self, mname, sauce):
        parsed_meme = commands.store.Parse(self.msg, self.content_type)
        parsed_meme['sauce'] = sauce
        memedict = { mname : parsed_meme }
        ins = commands.store.Insert(mname)
        if self.content_type in ('voice','video','document','audio','photo'): 
            return ins.file(memedict)
        elif self.content_type == 'text':
            return ins.quote(memedict)
    def send(self, mname):
        memesend = commands.send.getMeme(mname)
        print('going')
        if memesend:
            pass
        else:
            memesend = commands.send.getLegacyMeme(mname)
            if memesend:
                pass
            else:
                return False
        try:
            sendtype = memesend['mtype']
            sendfunc = 'send' + sendtype.capitalize()
            sendargs = [memesend['file_id']]
            sendkwargs = {'caption' : memesend.get('cap', None)}
        except KeyError:
            try:
                sendfunc = 'sendMessage'
                sendargs = [memesend['text'] + '\n <i>— ' + memesend['author'] + '</i>']
                sendkwargs = {'parse_mode' : 'html'}
            except KeyError:
                return False
        memeattrs = [sendfunc, sendargs, sendkwargs]
        print('blah')
        return memeattrs

