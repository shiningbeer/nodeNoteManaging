# -*- coding:utf-8 -*-

import os
import json
import datetime
import sys
import threading
from util.dao import daoNodeManager as dbo
from util.myLog import myLog
import logging
from time import sleep
from util.const import *

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from basicTask import basicTask
class zmapTask(basicTask):
    def run(self):
        task=self.task
        dbo=basicTask.dbo
        mylog=basicTask.mylog

        basicTask.taskCount+=1
        taskId = task[f_ID]
        strId = taskId.__str__()
        port = task[fPORT]
        ipRange = task[fIPRANGE]
        # start from progress
        progress = task[fPROGRESS]
        mylog.LogInJustScreen('start task: '+strId)
        count = -1
        for ip in ipRange:
            count = count+1
            if count < progress:
                continue
            try:
                os.system('zmap -p '+port+' -B 5M '+ip+' -o ./zr/'+strId)
            except:
                mylog.LogInJustScreen('Run Zmap Failed!')
                basicTask.taskCount-=1
                return

            for line in open('zr/'+strId, 'r'):
                line = line.strip()
                dbo.insert('taskResult--'+strId, {'re': line, 'sent': False})

            mylog.LogInJustScreen(str(count+1)+'/'+str(len(ipRange)))
            dbo.update('task', {f_ID: taskId}, {fPROGRESS: count+1})
            task_modi = dbo.findOne('task', {f_ID: taskId})
            paused = task_modi[fPAUSED]
            if paused:
                dbo.update('task', {f_ID: taskId}, {fRUNNING: False})
                basicTask.taskCount-=1
                return
        # zmap is complete
        mylog.LogInJustScreen('complete task: '+strId)
        dbo.update('task', {f_ID: taskId}, {fCOMPLETE: True, fRUNNING: False})
        basicTask.taskCount-=1

