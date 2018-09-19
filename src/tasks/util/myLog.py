import logging
from bson import ObjectId
import datetime
from const import *




# my logging class
class myLog(object):
    def __init__(self,logfile,dbo):
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(message)s",
            filename=logfile,
            filemode='a'
        )

        self.__dbo=dbo
        self.lastMsg=''
    def LogInScreenAndFileAndDB(self,tid,tname,tmsg,mark_err):        
        ''' log important event both in log file and the task's db keyLog field
        args:
            tid: task id, objectId
            tname:task name, string
            tmsg:the log msg,string
            mark_err: if mark the task as wrong, boolean
        '''
        # log content in file should be more specific
        logMsg='Task:'+tid.__str__()+'('+tname+')--'+tmsg
        nowTime=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        logging.info(logMsg)# log in file
        print nowTime+logMsg#log in screen
        # add to the task log
        self.__dbo.pushArray_task({f_ID:tid},{fKEYLOG:nowTime+tmsg})
        # mark the task as wrong
        if mark_err:
            self.__dbo.update_task({f_ID:tid},{fGOWRONG:True,fNEEDTOSYNC:True,fTHREADALLOT:0})

    def LogInFileAndScreen(self,msg):
        logging.info(msg)#log in file
        nowTime=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        print nowTime+msg#log in screen
    def LogInJustScreen(self,msg):
        if self.lastMsg==msg:            
            return
        nowTime=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        print nowTime+msg#log in screen
        self.lastMsg=msg


if __name__ == '__main__':
    from dao import daoNodeManager as dbo
    from bson import ObjectId
