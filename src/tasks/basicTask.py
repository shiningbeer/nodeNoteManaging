# -*- coding:utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class basicTask:
    taskCount = 0
    dbo=None
    mylog=None
    def __init__(self,task):
        self.task=task
    def run(self):
        print 'This should be overwritten by children classes.'
    


