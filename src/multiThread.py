# -*- coding:utf-8 -*-

import os
import json
import datetime
import sys
import threading
from time import sleep
from threading import Thread
import time


default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def runFuncWithTimeLimit(func,arg,timeout):
    ''' Putting func with time limitation.

    Args:
    	func:the func to be limited by timeout
    	arg: the arg taken by the func
    	timeout: time limitation by seconds
    Return:
    	result of the func
    '''
    class TimeoutException(Exception):
    	pass
    ThreadStop = Thread._Thread__stop
    class TimeLimited(Thread):
    	def __init__(self,_error= None,):
    		Thread.__init__(self)
    		self._error = _error
    		self.result=None
    	def run(self):
    		try:
    			self.result = func(*arg)
    		except Exception,e:
    			self._error =e
    	def _stop(self):
    		if self.isAlive():
    			ThreadStop(self)
    t = TimeLimited()
    t.start()
    t.join(timeout)
    if isinstance(t._error,TimeoutException):
    	t._stop()
    	print ('timeout')
    	return None
    if t.isAlive():
    	t._stop()
    	print ('timeout')
    	return None 
    if t._error is None:
    	return t.result 
    return None
class multiThread(object):

    def __init__(self, max_thread_count, work_func, lock_func):
        '''
        Args:
            -max_thread_count: the max thread count allowed
            -work_func: the thread function without involving shared resources
            -lock_func: shared resources involoved part of function codes, the first param of the func must be the result of work_func
        
        '''
    	self.__max_thread_count = max_thread_count
    	self.__present_thread_count = 0
    	self.__work_func= work_func
    	self.__lock_func = lock_func
    	self.__lock = threading.Lock()
    	self.__payloadList = []
    	self.__paramsList = []
    def dispatch(self, args_work,args_lock,payload,timeout):
    	''' use this function to create a thread with the params needed to pass to the thread functions
        Args:
             -args_work: args for the work_func
             -args_lock: args for the lock_func
             -payload: other params need to be processed by thread
             -timeout:the max time for running work_func
    	'''
    	def threadFunc(args_work,args_lock,payload):
            self.__payloadList.append(payload)#record the payload
            self.__paramsList.append(args_work)#record the args
            r = runFuncWithTimeLimit(self.__work_func,args_work,timeout)  #running the work_func with time limitation
            self.__lock.acquire()
            self.__lock_func(r,*args_lock)# running lock_func, the first param must be the result of work_func
            self.__present_thread_count=self.__present_thread_count- 1  # minus 1 for the thread count when this thread is over
            self.__payloadList.remove(payload)#remove the payload
            self.__paramsList.remove(args_work)#remove the args
            self.__lock.release()

    	# waiting until the threads pool is not full
        while True:
            if self.__present_thread_count>=self.__max_thread_count:
                sleep (1)
            else:
                break
        # add 1 to thread count
        self.__present_thread_count=self.__present_thread_count+1

    	t = threading.Thread(
    		target=threadFunc, args=(args_work,args_lock,payload))
    	t.start()

    def snapThreadPayloads(self):
        '''
        get the snap of payloads taken by the threads
        '''
        self.__lock.acquire()
        present_payload=[]
        for item in self.__payloadList:
            present_payload.append(item)
        self.__lock.release()
        return present_payload
    
    def snapThreadParams(self):
        '''
        get the snap of params given to the threads
        '''
        self.__lock.acquire()
        present_params=[]
        for item in self.__paramsList:
            present_params.append(item)
        self.__lock.release()
        return present_params
    def setMaxThreadCount(self,max_thread_count):
        self.__max_thread_count=max_thread_count

if __name__ == '__main__':
    #example
    def scan(x, y):
    	#print 'I\'m ' + str(x) + ',' + str(y)
        if y==3:
            sleep(70)
        else:
            sleep(3)
    	return x + y

    def record(r,f,i,y):
    	line=str(i)+','+str(y)+":"+str(r)+'\n'
    	f.writelines(line)
    	f.flush()

    dp = multiThread(25, scan, record)
    f = open('aaaa.txt', 'a')
    index=0
    for i in range(0, 10):		
    	for y in range(0, 10):
            index=index+1
            dp.dispatch((i, y),(f,i,y),index,60)
            print dp.snapThreadPayloads()
            print dp.snapThreadParams()
    sleep(13)
    f.close()
    print "ok"
