# -*- coding:utf-8 -*-
import os
import json
import sys
import threading
from util.dao import daoNodeManager as dbo
from util.myLog import myLog
from util.const import *

from time import sleep
from bson import ObjectId
import datetime
import time
import random
from util.multiThread import multiThread
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

'''
 CODE CONVENTION
 variable naming: with '_' between words, such as 'last_log'
 function naming: the start letter of each words should be captialized

'''
# set the format of logging and set the default logging level as info


# function copyed from internet. hexadecimal from 10 to 36
def hex36(num):
    # normal 36 hexadecimal36 should be '0123456789abcdefghijklmnopqrstuvwxyz'，the key here has been disordered
    key = 't5hrwop6ksq9mvf8xg3c4dzu01n72yeabijl'
    a = []
    while num != 0:
        a.append(key[num % 36])
        num = num / 36
    a.reverse()
    out = ''.join(a)
    return out

# function copyed from internet. get the unique id


def getId():
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


# initialize db operator
dbo = dbo()
mylog = myLog('./logs/plugin.mylog', dbo)
load_task_inteval = 3
run_task_count = 1
lock = threading.Lock()


def recordResult(result, id, ip,total,progress):
    '''
    record the result into database.
    this is the lock_func of multiThread class
    '''
    print total,progress+1
    if total==progress+1:
        dbo.update('task',{f_ID: ObjectId(id)}, {fCOMPLETE:True,fNEEDTOSYNC: True, fPROGRESS: total})
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
def decrementTaskLimit():
    global run_task_count
    lock.acquire()
    run_task_count = run_task_count-1
    lock.release()

def incrementTaskLimit():
    global run_task_count
    lock.acquire()
    run_task_count = run_task_count+1
    lock.release()
def doTask():


    # run limit
    global run_task_count

    if run_task_count <= 0:
        # mylog.LogInJustScreen('Threads Full! Can Not Load Any More Task!')
        return
    # get a task to run
    task = dbo.findOne('task', {fTYPE: 'plugin', fRUNNING: False,
                                fGOWRONG: False, fCOMPLETE: False, fPAUSED: False})
    # timer end case 1 : no task
    if task == None:
        mylog.LogInJustScreen('No Task Now!')
        return
    # if there is a task
    decrementTaskLimit()

    taskId = task[f_ID]
    strId = taskId.__str__()
    ipRange = task[fIPRANGE]
    total=len(ipRange)
    # start from progress
    progress = task[fPROGRESS]
    mylog.LogInJustScreen('start task: '+strId)
    index = -1
    # see if there are problems with plugin and zmap result.
    plugin = task[fPLUGIN][fNAME]
    # delete the .py extension
    plugin = plugin[0:len(plugin) - 3]
    try:
        exec("from plugins import " + plugin + " as scanning_plugin")
    # timer end case 2 : can't find plugin
    except:
        mylog.LogInJustScreen('can\'t find plugin: '+plugin)
        dbo.update('task',{f_ID:taskId},{fGOWRONG:True})
        incrementTaskLimit()
        # end of this fucntion and thus the timer
        return
    # timer end case 3 plugin does not has the scan function
    if not scanning_plugin.scan:
        mylog.LogInJustScreen('plugin: ' +
                              plugin+' have no scan function!')
        incrementTaskLimit()
        return
    # it is comfired the task can be run,  set the task is running
    dbo.update_task({f_ID: taskId}, {fRUNNING: True, fNEEDTOSYNC: True})

    dp = multiThread(100, scanning_plugin.scan, recordResult)
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
                incrementTaskLimit()
                return
        dp.dispatch((ip,), (strId, ip,total,index), index, 120)

    # timer end case 4,all ip dispatched 
    incrementTaskLimit()

if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # when startup, all the tasks should not be running
    dbo.update('task', {fRUNNING: True}, {fRUNNING: False})
    # set the global variables from the db
    load_task_inteval = 3
    run_task_count = 1
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0, doTask)
        timer.start()
        sleep(load_task_inteval)
