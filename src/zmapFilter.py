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
        # mylog.LogInJustScreen('Waiting other task to be done')
        return
    task=dbo.getOne_task({fZMAPRUNNING:False,fGOWRONG:False,fZMAPCOMPLETE:False,fPAUSED:False})

    # if no task, print the msg and end this
    if task == None:
        mylog.LogInJustScreen('No Task Now!')
        return    
    # if there is a task 
    decrementZmapLimit()
    id=task[f_ID]
    task_name=task[fTASKNAME]
    strid=task[f_ID].__str__()
    nodeTaskId=task[fNODETASKID]
    plugin=task[fPLUGIN]
    port=plugin['port']
    ipRange=task[fZMAPRANGE]
    total=task[fZMAPTOTAL]
    # start from progress
    progress=task[fZMAPPROGRESS]

    mylog.LogInScreenAndFileAndDB(id,task_name,'Zmap Work Run.',False)

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

        dbo.saveResult(nodeTaskId+'zr',{'ip':count+1,'sent':False})
        sleep(0.1)
        mylog.LogInJustScreen('Total Progress:  '+str(count+1)+'/'+str(total))
        dbo.update_task({f_ID:id},{fZMAPPROGRESS:count+1,fNEEDTOSYNC:True})
        task_modi=dbo.getOne_task_limit_fields({f_ID:id},{fPAUSED:1})
        paused=task_modi[fPAUSED]
        if paused:
            mylog.LogInScreenAndFileAndDB(id,task_name,'Zmap Work Paused.',False)
            incrementZmapLimit()
            # exit timer when paused
            return
    # zmap is complete
    dbo.update_task({f_ID:id},{fZMAPCOMPLETE:True,fNEEDTOSYNC:True})
    mylog.LogInScreenAndFileAndDB(id,task_name,'Zmap Work complete.',False)
    incrementZmapLimit()
   
if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # at the start, set all task no running zmap
    dbo.update_task({fZMAPRUNNING:True},{fZMAPRUNNING:False,fNEEDTOSYNC:True})
    task_inteval=3
    run_zmap_count=1
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0,zmapwork)
        timer.start()
        sleep(task_inteval)
