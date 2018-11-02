# -*- coding:utf-8 -*-
import os
import json
import sys
import threading
from util.dao import daoNodeManager as dbo
from util.myLog import myLog
from util.const import *
from util.utilFunc import *
from time import sleep
from bson import ObjectId
import datetime
import time
from util.multiThread import multiThread
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


from basicTask import basicTask

def getScan(plugin):

    try:
        exec("from plugins import " + plugin + " as scanning_plugin")
    except:
        print 'kdkdkd'
        return None
    return scanning_plugin.scan

class pluginTask(basicTask):
    def run(self):
        task=self.task
        dbo=self.dbo
        mylog=self.mylog
        def recordResult(result, id, ip,total,progress):
            '''
            record the result into database.
            this is the lock_func of multiThread class
            '''
            print total,progress+1
            if total==progress+1:
                dbo.update('task',{f_ID: ObjectId(id)}, {fCOMPLETE:True, fPROGRESS: total})
                mylog.LogInJustScreen('task complete')
            if result != None and result != {}:
                convert2unicode(result)
                re = {'ip': ip, 'scanTime': int(time.time()), 'data': result}
                rest={'re': re,'sent': False}
                try:
                    dbo.insert('taskResult--'+id, rest)
                except:
                    rid = getId()
                    rest['_id'] = ObjectId(rid)
                    dbo.insert('taskResult--'+id, rest)


        taskId = task[f_ID]
        strId = taskId.__str__()
        ipRange = task[fIPRANGE]
        total=len(ipRange)
        # start from progress
        progress = task[fPROGRESS]
        mylog.LogInJustScreen('start task: '+strId)
        index = -1
        # see if there are problems with plugin and zmap result.
        plugin = task[fPLUGIN]['name']
        # delete the .py extension
        plugin = plugin[0:len(plugin) - 3]
        scan=getScan(plugin)
        if scan==None:
            dbo.update('task',{f_ID:taskId},{fGOWRONG:True})
            mylog.LogInJustScreen('cannot find plugin')
            basicTask.taskCount-=1
            return
        # it is comfired the task can be run,  set the task is running
        dbo.update('task',{f_ID: taskId}, {fRUNNING: True })

        dp = multiThread(200, scan, recordResult)
        stepCounter = 0
        for ip in ipRange:
            index = index+1
            stepCounter = stepCounter+1
            if index < progress:
                continue
            sleep(0.5)
            if stepCounter == 20:
                stepCounter=0
                mylog.LogInJustScreen(str(index+1)+'/'+str(len(ipRange)))
                dbo.update('task', {f_ID: taskId}, {fPROGRESS: index+1})
                task_modi = dbo.findOne('task', {f_ID: taskId})
                paused = task_modi[fPAUSED]
                if paused:
                    r = dp.snapThreadPayloads()
                    if r != None:
                        least = r[0]
                        for item in r:
                            if item < least:
                                least = item
                        dbo.update('task',{f_ID: id}, {fPROGRESS: least})
                    dbo.update('task', {f_ID: taskId}, {fRUNNING: False})
                    basicTask.taskCount-=1
                    return
            dp.dispatch((ip,), (strId, ip,total,index), index, 120)

        # timer end case 4,all ip dispatched 
        basicTask.taskCount-=1


