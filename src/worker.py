# -*- coding:utf-8 -*-
import os
import json
import sys
import threading
from dao import daoNodeManager as dbo
from const import *
import logging
from time import sleep
from bson import ObjectId
import datetime,time,random
from multiThread import multiThread
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
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    filename='./worklog.log',
    filemode='a'
)


# function copyed from internet. hexadecimal from 10 to 36
def hex36(num):
    # normal 36 hexadecimal36 should be '0123456789abcdefghijklmnopqrstuvwxyz'，the key here has been disordered
    key='t5hrwop6ksq9mvf8xg3c4dzu01n72yeabijl'
    a = []
    while num != 0:
        a.append(key[num%36])
        num = num / 36
    a.reverse()
    out = ''.join(a)
    return out

# function copyed from internet. get the unique id
def getId():
    d1=datetime.datetime(2015,1,1)
    d2=datetime.datetime.now()
    s=(d2-d1).days*24*60*60
    ms=d2.microsecond
    id1=hex36(random.randint(36, 1295))
    id2=hex36(s)
    id3=hex36(ms+46656)

    mId=id1+id2+id3
    return mId[::-1] 

# function copyed from internet. convert all strings in a dict to unicode
def convert2unicode(mydict):
    for k, v in mydict.iteritems():
        if isinstance(v, str):
            mydict[k] = unicode(v, errors = 'replace')
        elif isinstance(v, dict):
            convert2unicode(v)

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


# initialize the database operator
dbo=dbo()
mylog=logMsg('')
# global variables
useable_threads=100
def recordResult(result,tableName,ip):
    '''
    record the result into database.
    this is the lock_func of multiThread class
    '''
    if result!=None and result!={}:
        convert2unicode(result)
        rest={'ip':ip,'scanTime':int(time.time()),'data':result}
        try:
            dbo.saveResult(tableName,result)
        except:
	    print result
            id=getId()
            result['_id']=ObjectId(id) 
            dbo.saveResult(tableName,result)
def importantLog(tid,tname,tmsg,mark_err):        
    ''' log important event both in log file and the task's db keyLog field
    args:
        tid: task id, objectId
        tname:task name, string
        tmsg:the log msg,string
        mark_err: if mark the task as wrong, boolean
    '''
    # log in file
    logMsg='Task:'+tid.__str__()+'('+tname+')--'+tmsg
    mylog.log(logMsg)
    # add to the task log
    nowTime=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    dbo.pushArray_task({f_ID:tid},{fKEYLOG:nowTime+tmsg})
    # mark the task as wrong
    if mark_err:
        dbo.update_task({f_ID:tid},{fIMPLSTATUS:sWRONG,fNEEDTOSYNC:True,fTHREADALLOT:0})
    print nowTime+logMsg
def doTask():
    '''
    get suitable tasks to run
    '''

    global useable_threads,record_step
    ##### timer end case 1: threads are full
    if useable_threads<=0:
        mylog.log('Threads Full! Can Not Load Any More Task!')
        # end of the func thus the timer
        return
    # get a task to run
    task=dbo.getOne_task({fOPERSTATUS:sRUN,fIMPLSTATUS:sWAITING,fZMAPSTATUS:sCOMPLETE})

    ##### timer end case 2: no task to run
    if task == None:
        mylog.log('No Task Now!')
        # end of the func thus the timer
        return

    
    # see if there are problems with plugin and zmap result.
    strid=task[f_ID].__str__()
    task_name=task[fTASKNAME]
    node_task_id=task[fNODETASKID]
    plugin=task[fPLUGIN][fNAME]
    # delete the .py extension
    plugin = plugin[0:len(plugin) - 3]
    iptotal=task[fIPTOTAL]
    progress=task[fPROGRESS]
    try:
        exec("from plugins import " + plugin + " as scanning_plugin")
    ##### timer end case 3 : can't find plugin
    except:
        importantLog(id,task_name,'can\'t find plugin: '+plugin,True)
        # end of this fucntion and thus the timer
        return
    ##### timer end case 4 plugin does not has the scan function
    if not scanning_plugin.scan:
        importantLog(id,task_name,'plugin: '+plugin+' have no scan function!',True)
        # end of this fucntion and thus the timer
        return
    ##### timer end case 5 can't find zmap result file
    if not os.path.exists('./zr/'+strid):
        importantLog(id,task_name,'cant find zmap result file!',True)
        # end of this fucntion and thus the timer
        return
    # compute the thread count
    id=task[f_ID]
    thread_demand=task[fTHREADDEMAND]
    thread_allot=0
    if thread_demand>=useable_threads:
        # allot all the available to this task
        
        thread_allot=useable_threads
        useable_threads=0
    else:
        # allot its demand count
        thread_allot=thread_demand
        useable_threads=useable_threads-thread_demand
    # it is comfired the task can be run, so adjust thread count, set the task is running
    dbo.update_task({f_ID:id},{fTHREADALLOT:thread_allot,fIMPLSTATUS:sRUNNING,fNEEDTOSYNC:True})

    # do the job, log first                
    importantLog(id,task_name,'Run with '+str(thread_allot)+' threads',False)
    # use mutiple threads to run the plugin's scan to do this job
    dp=multiThread(thread_allot,scanning_plugin.scan,recordResult)
    index=0   
    stepCounter=0
    for line in  open('zr/'+strid, 'r'):       
        line=line.strip()
        # start from progress        
        index=index+1
        if index<progress:
            continue
        # one thread is dispatched to one line of ip, the params here are passed to thread functions
        dp.dispatch((line,),(node_task_id,line),index,20)
        stepCounter=stepCounter+1
        # record the progress,every the count of useable_threads
        if stepCounter==useable_threads:
            r=dp.snapThreadPayloads() # take the payloads all the thread is taking presently
            # find the least
            if r!=None:
                least=r[0]
                for item in r:                    
                    if item<least:
                        least=item
                dbo.update_task({f_ID:id},{fPROGRESS:least,fNEEDTOSYNC:True})
            stepCounter=0

            # look for any modification of the task instruction or params
            task_modi=dbo.getOne_task({f_ID:id})
            ##### timer end case 6 : task paused by new instruction
            if task_modi[fOPERSTATUS]!=sRUN:
                importantLog(id,task_name,'Paused.',False)
                # record progress
                r=dp.snapThreadPayloads()
                if r!=None:
                    least=r[0]
                    for item in r:                    
                        if item<least:
                            least=item
                    dbo.update_task({f_ID:id},{fPROGRESS:least,fNEEDTOSYNC:True,fIMPLSTATUS:sWAITING,fTHREADALLOT:0})
                useable_threads=100    
                return
            new_demand=task_modi[fTHREADDEMAND]
            # thread demand modified 
            if new_demand!=thread_demand:
                if new_demand<thread_allot:
                    surplus=thread_allot-new_demand 
                    useable_threads=useable_threads+surplus 
                    dp.setMaxThreadCount(new_demand)
                    thread_allot=new_demand
                if new_demand>thread_allot:
                    if new_demand-thread_allot>=useable_threads:
                        thread_allot=thread_allot+useable_threads 
                        useable_threads=0
                    else:
                        additional=new_demand-thread_allot 
                        useable_threads=useable_threads-additional 
                        thread_allot=thread_allot+additional
                thread_demand=new_demand
                dbo.update_task({f_ID:id},{fTHREADALLOT:thread_allot,fNEEDTOSYNC:True})
                importantLog(id,task_name,'Threads changed to '+str(thread_allot)+'.',False)
                    

    # task complete! change the status
    dbo.update_task({f_ID:id},{fIMPLSTATUS:sCOMPLETE,fOPERSTATUS:sCOMPLETE,fNEEDTOSYNC:True,fPROGRESS:iptotal,fTHREADALLOT:0})
    useable_threads=100
    ##### timer end case 7: task completed!!


if __name__ == '__main__':
    # todo:only one sample of this programme should be run
    # when startup, all the tasks should not be running
    dbo.update_task({fIMPLSTATUS:sRUNNING},{fIMPLSTATUS:sWAITING,fTHREADALLOT:0,fNEEDTOSYNC:True})
    # set the global variables from the db
    load_task_inteval=3
    
    useable_threads=100
    # every inteval,start a timer to find a task to run
    while True:
        timer = threading.Timer(0,doTask)
        timer.start()
        sleep(load_task_inteval)

