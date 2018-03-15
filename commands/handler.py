import telepot
import commands.store
import commands.send
import commands.lister
import commands.sauce

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
            return ins.mfile(memedict)
        elif self.content_type == 'text':
            return ins.quote(memedict)
    
    def send(self, mname):
        memesend = commands.send.getMeme(mname)
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
        return memeattrs

    def sauce(self, mname=None):
        def byName(mname):
            memedict = commands.send.getMeme(mname)
            try:
                author = memedict['sauce']
            except KeyError:
                return False
            return author
        def byRef():
            memeobj = commands.store.Parse(self.msg, self.content_type)
            try:
                memeid = memeobj['file_id']
                mname = commands.sauce.getMemeById(memeid)
                memedict = commands.send.getMeme(mname)
            except KeyError:
                memetext = memeobj['text']
                mname = commands.sauce.getMemeByText(memetext)
                memedict = commands.send.getMeme(mname)
            try:
                author = memedict['sauce']
                return author
            except KeyError:
                return False
        if mname is not None:
            return byName(mname)
        elif mname is None:
            return byRef()

