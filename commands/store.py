import settings
import json

memeindex = settings.PROJECT_ROOT + '/memeindex.json'

def Parse(msg, content_type):
    memedict = {}
    if content_type in ('voice','video','document','audio'):
        m = msg.get(content_type, {})
        memedict['file_id'] = m.get('file_id')
        memedict['thumb_id'] = m.get('thumb', {}).get('file_id')
        memedict['cap'] = msg.get('caption', '')
        memedict['mtype'] = content_type
    elif content_type == 'photo':
        m = msg.get(content_type)
        memedict['file_id'] = m[-1]['file_id']
        memedict['thumb_id'] = m[0]['file_id']
        memedict['cap'] = msg.get('caption', '')
        memedict['mtype'] = content_type
    elif content_type == 'text':
        memedict['text'] = msg.get('text')
        try:
            memedict['author'] = '@' + msg['forward_from']['username']
        except KeyError:
            memedict['author'] = '@' + msg['from']['username']
    else:
        raise Exception('MsgObjError')
    return memedict

class Insert:

    def __init__(self, mname):
        with open(memeindex, 'r') as f:
            self.memefeed = json.load(f)
        self.mname = mname
    
    def file(self, memedict):
        self.memefeed['files'].update(memedict)
        with open(memeindex, 'w') as mi:
            json.dump(memefeed, mi, indent=2)
        return True

    def quote(memedict):
        memefeed['quotes'].update(memedict)
        with open(memeindex, 'w') as mi:
            json.dump(memefeed, mi, indent=2)
        return True


