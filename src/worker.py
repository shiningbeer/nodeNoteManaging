# -*- coding:utf-8 -*-
import os
import json
import sys
import threading
from dao import daoNodeManager as dbo
import logging
from time import sleep
from bson import ObjectId
from multiThread import multiThread
# 设置默认的level为DEBUG
# 设置log的格式
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s"
)

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

import datetime,time,random

#10进制转换36进制
def hex36(num):
    # 正常36进制字符应为'0123456789abcdefghijklmnopqrstuvwxyz'，这里我打乱了顺序
    key='t5hrwop6ksq9mvf8xg3c4dzu01n72yeabijl'
    a = []
    while num != 0:
        a.append(key[num%36])
        num = num / 36
    a.reverse()
    out = ''.join(a)
    return out

#获取唯一标识
def getId():
    #36进制位数对应10进制数范围参考：
    #1位：0-35
    #2位：36-1295
    #3位：1296-46655
    #4位：46656-1679615
    #5位：1679616-60466175
    #6位：60466176-2176782335

    # 只要秒数大于60466175，就可以转换出6位的36进制数，这里从2015年1月1日开始计算，约70年后会变成7位
    d1=datetime.datetime(2015,1,1)
    d2=datetime.datetime.now()
    #获取秒数
    s=(d2-d1).days*24*60*60
    #获取微秒数
    ms=d2.microsecond
    #随机两位字符串
    id1=hex36(random.randint(36, 1295))
    #转换秒数
    id2=hex36(s)
    #转换微秒数，加46656是为了保证达到4位36进制数
    id3=hex36(ms+46656)

    mId=id1+id2+id3
    return mId[::-1] 


def convert2unicode(mydict):
    for k, v in mydict.iteritems():
        if isinstance(v, str):
            mydict[k] = unicode(v, errors = 'replace')
        elif isinstance(v, dict):
            convert2unicode(v)


dbo=dbo()
task_inteval=3
thread_count=100
record_step=2*thread_count
def recordResult(result,tableName,ip):
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


def work(printed):
    task = dbo.get_one_task_to_execute()
    r = u'No Task Now!'
    # 如果无任务，打印信息，定时下一次执行
    if task == None:
        if printed != r:
            logging.info(r)
            printed = r
        timer = threading.Timer(task_inteval,work, (printed,))
        timer.start()
        return
    # 如果有任务
    id=task['id']
    nodetaskid=task['nodeTaskId']
    plugin=task['plugin']['name']
    plugin = plugin[0:len(plugin) - 3]
    ipTotal=task['ipTotal']
    r = u'Task:'+id+u'cant find plugin. :'+plugin
    try:
        exec("from plugins import " + plugin + " as scanning_plugin")
    # 如果未找到插件(执行exec出错)，则打印信息，定时下一次执行
    except:
        if printed != r:
            logging.info(r)
            printed = r
        dbo.modi_implStatus_by_id(id,-1,'can\'t find plugin')
        timer = threading.Timer(task_inteval,work, (printed,))
        timer.start()
        return

    if os.path.exists('./zr/'+id):
        logging.info(u'Implement task:'+id)
        dp=multiThread(thread_count,scanning_plugin.scan,recordResult)
        index=0   
        stepCounter=0
        resumeIndex=dbo.get_progress(id)        
        for line in  open('zr/'+id, 'r'):       
            line=line.strip()
            logging.info
            #寻找到上次的进度        
            index=index+1
            if index<=resumeIndex:
                continue
            #分派任务给线程        
            dp.dispatch((line,),(nodetaskid,line),index)
            stepCounter=stepCounter+1
            #每扫描record_step个记录一次进度
            if stepCounter==record_step:
                r=dp.getAllThreadIndex()#获取每个线程执行到哪
                #取得最小
                least=r[0]
                for item in r:                    
                    if item<least:
                        least=item
                dbo.record_progress(id,least)
                print least
                stepCounter=0
            #查看任务指令是否变化
            newImpl=dbo.get_new_operStatus(id)
            if newImpl!=1:
                #记录执行进度
                r=dp.getAllThreadIndex()
                if r!=None:
                    least=r[0]
                    for item in r:                    
                        if item<least:
                            least=item
                    dbo.record_progress(id,least)
                #定时下次执行
                timer = threading.Timer(task_inteval, work,('',))
                timer.start()
                #退出本次执行
                return

         #修改状态为完成
        dbo.modi_implStatus_by_id(id,1,'')
        dbo.record_progress(id,ipTotal)
        # 完成一个后，直接执行下一个
        timer = threading.Timer(0, work,('',))
        timer.start()
    else:
        logging.info(u'Error!')
        #修改Status为出错，errMsg为can't find zmap result  
        dbo.modi_implStatus_by_id(id,-1,'can\'t find zmap result!')
        timer = threading.Timer(task_inteval,work, (printed,))
        timer.start()
    

def doWork():
    timer = threading.Timer(0, work,('',))
    timer.start()


if __name__ == '__main__':
    doWork()
