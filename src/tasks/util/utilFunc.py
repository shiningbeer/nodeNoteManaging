import sys
import datetime
import random
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
# function copyed from internet. get the unique id
def getId():
    # function copyed from internet. hexadecimal from 10 to 36
    def hex36(num):
        key = 't5hrwop6ksq9mvf8xg3c4dzu01n72yeabijl'
        a = []
        while num != 0:
            a.append(key[num % 36])
            num = num / 36
        a.reverse()
        out = ''.join(a)
        return out
    d1 = datetime.datetime(2015, 1, 1)
    d2 = datetime.datetime.now()
    s = (d2-d1).days*24*60*60
    ms = d2.microsecond
    id1 = hex36(random.randint(36, 1295))
    id2 = hex36(s)
    id3 = hex36(ms+46656)

    mId = id1+id2+id3
    return mId[::-1]

# function copyed from internet. convert all strings in a dict to unicode
def convert2unicode(mydict):
    for k, v in mydict.iteritems():
        if isinstance(v, str):
            mydict[k] = unicode(v, errors='replace')
        elif isinstance(v, dict):
            convert2unicode(v)