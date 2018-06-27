# -*- coding:utf-8 -*-

import os
import json
import datetime
import sys
import threading
from dao import daoNodeManager as dbo
import logging
from time import sleep
from const import *

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# set the format of logging and set the default logging level as info
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    filename='./worklog.log',
    filemode='a'
)
# my logging class
class logMsg(object):
    '''
    log the msg not repeatedly
    '''
    def __init__(self,last_log):
        self.last_log=last_log
    def log(self,msg):
        if self.last_log!=msg:
            logging.info(msg)
            self.last_log = msg
            print msg

# initialize db operator
dbo=dbo()
mylog=logMsg('')
task_inteval=3
run_zmap_count=1
def zmapwork():
    def markTaskErr(id,err_msg):        
        ''' mark the task as err and record the err msg
        args:
            id: task id
            err_msg: the err msg need to logging
        '''
        mylog.log(err_msg)
        
        # mark the task as wrong
        dbo.update_task({f_ID:id},{fZMAPSTATUS:sWRONG,fNEEDTOSYNC:True})
        # add to the task log
        dbo.pushArray_task({f_ID:id},{fKEYLOG:err_msg})

    # zmap run limit
    run_zmap_count=run_zmap_count-1
    if run_zmap_count<0:
        mylog.log('Waiting other task to be done')
        return

    task=dbo.getOne_task({fOPERSTATUS:sRUN,fZMAPSTATUS:sWAITING})

    # if no task, print the msg and end this
    if task == None:
        mylog.log('No Task Now!')
        return
    # if there is a task 
    id=task['id']
    nodeTaskId=task['nodeTaskId']
    plugin=task['plugin']
    port=plugin['port']
    if os.path.exists('./targets/'+nodeTaskId):
        mylog.log(u'Implement Zmap Task:'+id)
        # use system command to run zmap
        try:
            os.system('zmap -p '+port+' -B 5M -w ./targets/'+nodeTaskId+' -o ./zr/'+id)
        except:
            mylog.log('can\'t run zmap, please ensure zmap is installed!')
            return
        
        # compute the count of the result
        count=0
        for line in  open('zr/'+id, 'r'): 
            count=count+1
        # after work done, mark the task that zmap has finished, and store the count of result
        dbo.update_task({f_ID:id},{fZMAPSTATUS:sCOMPLETE,fIPTOTAL:count,fNEEDTOSYNC:True})
    else:
        markTaskErr(id,'Error, cant find ip file!:/targets/'+nodeTaskId)

if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # at the start, set all task no running zmap
    dbo.update_task({fZMAPSTATUS:{'$ne':sRUNNING}},{fZMAPSTATUS:sWAITING,fNEEDTOSYNC:True})
    task_inteval=3
    run_zmap_count=1
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0,zmapwork)
        timer.start()
        sleep(task_inteval)
