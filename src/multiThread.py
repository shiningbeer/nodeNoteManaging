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


def working_with_timeout(self,func,arg,timeout):
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
        -lock_func: shared resources involoved part of function codes
    
    '''
    	self.max_thread_count = max_thread_count
    	self.present_thread_count = 0
    	self.work_func= work_func
    	self.lock_func = lock_func
    	self.lock = threading.Lock()
    	self.__payloadList = []
    	self.__paramsList = []
    def dispatch(self, args_work,args_lock,payload):
    	''' use this function to create a thread with the params needed to pass to the thread functions
        Args:
             -args_work: args for the work_func
             -args_lock: args for the lock_func
             -payload: other params need to be processed by thread
    	'''

        
    	def threadFunc(queueIndex, args_runFunc,args_lock,index):
    		self.queue[queueIndex]['params'] = args_runFunc
    		self.queue[queueIndex]['index'] = index
    		r = self.__runFunc(self.runFunc,args_runFunc,60)  # 执行函数
    		# print str(args_runFunc) + '退出了'
    		self.lock.acquire()
    		self.lock_func(r,*args_lock)
    		self.threadCount = self.threadCount - 1  # 退出时，线程数量-1
    		self.threadFull = False  # 退出了一个，线程肯定不满了
    		# 退出时设置队列可用，执行进度记录一下
    		self.queue[queueIndex]['available'] = True

    		self.lock.release()

    	# 线程个数+1,如果个数与最大个数相等，说明满了。
    	self.threadCount = self.threadCount + 1
    	if self.threadCount == self.maxThread:
    		self.threadFull = True
    	while self.threadFull:
    		sleep(0.5)
    	# 取得空队列
    	queueIndex = None
    	while queueIndex == None:
    		for i in range(0, self.maxThread):
    			if self.queue[i]['available']:
    				queueIndex = i
    				break
    	# 新建一个线程加入队列,由于队列并不需要了解哪个线程加入队列，只要将队列设置成false表示当前队列不可用即可。
    	self.queue[queueIndex]['available'] = False
    	# 将队列index传给线程，使得它可以在线程退出时设置当前队列执行到哪里
    	t = threading.Thread(
    		target=threadFunc, args=(queueIndex, args_runFunc,args_lock,index))
    	t.start()

    def getAllPayload(self):
    	return self.__payloadList
    def getAllParams(self):
    	return self.__paramsList

if __name__ == '__main__':
    #例子
    def scan(x, y):
    	# print '我是' + str(x) + ',' + str(y)
    	# pass
    	if x>5:
    		sleep(3)
    	return x + y

    def record(r,f,i,y):
    	line=str(i)+','+str(y)+":"+str(r)+'\n'
    	f.writelines(line)
    	f.flush()

    dp = multiThread(5, scan, record)
    f = open('aaaa.txt', 'a')
    for i in range(0, 10):		
    	for y in range(0, 10):
    		while dp.threadFull:
    			sleep(0.1)
    		dp.dispatch((i, y),(f,i,y),(i,y))
    	print dp.getAllThreadIndex()
    sleep(3)
    f.close()
    print "ok"
