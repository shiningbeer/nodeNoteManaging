# -*- coding:utf-8 -*-

import os
import json
import datetime
import sys
import threading
from dao import daoNodeManager as dbo
from myLog import myLog
import logging
from time import sleep
from const import *

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# initialize db operator
dbo=dbo()
mylog=myLog('./zmap.mylog',dbo)
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
        mylog.commonLog('Waiting other task to be done')
        return

    task=dbo.getOne_task({fOPERSTATUS:sRUN,fZMAPSTATUS:sWAITING})

    # if no task, print the msg and end this
    if task == None:
        mylog.commonLog('No Task Now!')
        return
    # if there is a task 
    decrementZmapLimit()
    id=task[f_ID]
    task_name=task[fNAME]
    strid=task[f_ID].__str__()
    nodeTaskId=task[fNODETASKID]
    plugin=task[fPLUGIN]
    port=plugin['port']
    if os.path.exists('./targets/'+nodeTaskId):
        mylog.importantLog(id,task_name,'Run Zmap.',False)
        # use system command to run zmap
        try:
            os.system('zmap -p '+port+' -B 5M -w ./targets/'+nodeTaskId+' -o ./zr/'+strid)
        except:
            mylog.importantLog(id,task_name,'Run Zmap Failed!',True)
            incrementZmapLimit()
            return
        
        # compute the count of the result
        count=0
        for line in  open('zr/'+strid, 'r'): 
            count=count+1
        # after work done, mark the task that zmap has finished, and store the count of result
        dbo.update_task({f_ID:id},{fZMAPSTATUS:sCOMPLETE,fIPTOTAL:count,fNEEDTOSYNC:True})
        incrementZmapLimit()
    else:
        mylog.importantLog(id,task_name,'Can\'t find ip target file: ./targets/'+nodeTaskId)
        incrementZmapLimit()

if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # at the start, set all task no running zmap
    dbo.update_task({fZMAPSTATUS:sRUNNING},{fZMAPSTATUS:sWAITING,fNEEDTOSYNC:True})
    task_inteval=3
    run_zmap_count=1
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0,zmapwork)
        timer.start()
        sleep(task_inteval)
