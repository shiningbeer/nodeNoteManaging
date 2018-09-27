# -*- coding:utf-8 -*-
import os
import json
import sys
import threading
from util.dao import daoNodeManager as dbo
from util.myLog import myLog
from util.const import *

from basicTask import basicTask
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


from pluginTask import pluginTask
from zmapTask import zmapTask
def taskSelector(task):
    if task['type']=='zmap':
        return zmapTask(task)
    if task['type']=='plugin':
        return pluginTask(task)

# initialize
dbo = dbo()
if not os.path.exists('./logs'):
    os.makedirs('./logs')
mylog = myLog('./logs/task.mylog', dbo)
basicTask.dbo=dbo
basicTask.mylog=mylog
basicTask.taskCount=0
if not os.path.exists('./zr'):
    os.makedirs('./zr')


def runTask(limit):
    # run limit
    if basicTask.taskCount>=limit:
        return 

    # # get a task to run
    tk = dbo.findOne('task', {fRUNNING: False, fGOWRONG: False, fCOMPLETE: False, fPAUSED: False})
    if tk == None:
        mylog.LogInJustScreen('No Task Now!')
        return

    task=taskSelector(tk)
    task.run()

if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # when startup, all the tasks should not be running
    dbo.update('task', {fRUNNING: True}, {fRUNNING: False})
    # set the global variables from the db
    run_task_limit=1
    load_task_inteval = 3
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0, runTask,(run_task_limit,))
        timer.start()
        sleep(load_task_inteval)
