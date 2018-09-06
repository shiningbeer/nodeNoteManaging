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

# initialize db operator
dbo=dbo()
mylog=myLog('./logs/zmap.mylog',dbo)
task_inteval=3
run_zmap_count=1
lock=threading.Lock()
def zmapwork():
    def decrementZmapLimit():
        global run_zmap_count
        lock.acquire()
        run_zmap_count=run_zmap_count-1
        lock.release()

    def incrementZmapLimit():
        global run_zmap_count
        lock.acquire()
        run_zmap_count=run_zmap_count+1
        lock.release()
    
    # zmap run limit
    global run_zmap_count
    if run_zmap_count<=0:
        # mylog.LogInJustScreen('Waiting other task to be done')
        return
    task=dbo.findOne('task',{fRUNNING:False,fGOWRONG:False,fCOMPLETE:False,fPAUSED:False})
    # if no task, print the msg and end this
    if task == None:
        # mylog.LogInJustScreen('No Task Now!')
        return    
    # if there is a task 
    decrementZmapLimit()
    taskId=task[f_ID]
    strId=taskId.__str__()
    port=task[fPORT]
    ipRange=task[fIPRANGE]
    # start from progress
    progress=task[fPROGRESS]
    mylog.LogInJustScreen('start task: '+strId)
    count=-1
    for ip in ipRange:
        count=count+1        
        if count<progress:
            continue
        # try:
        #     os.system('zmap -p '+port+' -B 5M '+ip+' -o ./zr/'+strid)
        # except:
        #     mylog.LogInScreenAndFileAndDB(id,task_name,'Run Zmap Failed!',True)
        #     incrementZmapLimit()
        #     # exit timer when meets error
        #     return

        # for line in  open('zr/'+strid, 'r'):
        #     line=line.strip()
        #     dbo.saveResult(nodeTaskId+'zr',{'ip':line,'sent':False})
        sleep(0.5)
        for i in range(8):
            dbo.insert('taskResult--'+strId,{'re':ip+'--'+str(i),'sent':False})        
        mylog.LogInJustScreen(str(count+1)+'/'+str(len(ipRange)))
        dbo.update('task',{f_ID:taskId},{fPROGRESS:count+1})
        task_modi=dbo.findOne('task',{f_ID:taskId})
        paused=task_modi[fPAUSED]
        if paused:
            dbo.update('task',{f_ID:taskId},{fRUNNING:False})
            incrementZmapLimit()
            # exit timer when paused
            return
    # zmap is complete
    mylog.LogInJustScreen('complete task: '+strId)
    dbo.update('task',{f_ID:taskId},{fCOMPLETE:True,fRUNNING:False})
    incrementZmapLimit()
   
if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # at the start, set all task no running zmap
    dbo.update('task',{fRUNNING:True},{fRUNNING:False})
    task_inteval=3
    run_zmap_count=1
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0,zmapwork)
        timer.start()
        sleep(task_inteval)
