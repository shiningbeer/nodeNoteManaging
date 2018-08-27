# -*- coding:utf-8 -*-
from abc import ABCMeta, abstractmethod
from pymongo import MongoClient as mc
from bson import ObjectId
import pymongo
import datetime
import sys
from const import *

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

TASK='task'
class daoNodeManager(object):
    # 构造时连接数据库
    def __init__(self):
        self.client = mc()
        self.db = self.client.nodeDBDev2
    def update(self,col,find_dict,update_dict):
        coll=self.db[col]
        return coll.update_many(find_dict, {"$set":update_dict })

    def findOne(self,col,find_dict):
        coll=self.db[col]
        return coll.find_one(find_dict)

    def insert(self,tableName,document):
        coll=self.db[tableName]
        coll.insert_one(document)



    def update_task(self,find_dict,update_dict):
        coll=self.db[TASK]
        return coll.update_many(find_dict, {"$set":update_dict })
    
    def pushArray_task(self,find_dict,push_dict):
        coll=self.db[TASK]
        return coll.update_many(find_dict, {"$push":push_dict })


    def getOne_task(self,find_dict):
        coll=self.db[TASK]
        cur = coll.find(find_dict)
        tks = []
        for d in cur:
            tks.append(d)
        if len(tks)==0:
            return None
        return tks[0]
    def getOne_task_limit_fields(self,find_dict,field_dict):
        coll=self.db[TASK]
        cur = coll.find(find_dict,field_dict)
        tks = []
        for d in cur:
            tks.append(d)
        if len(tks)==0:
            return None
        return tks[0]

    def saveResult(self,tableName,document):
        coll=self.db[tableName]
        coll.insert_one(document)

    def resetZmap(self):
        coll = self.db.task
        return coll.update_many({}, {"$set": {'zmapProgress': 0,'zmapComplete': False}})


    def resetNeedToSync(self):
        coll = self.db.task
        return coll.update_many({}, {"$set": {'needToSync':True}})
    def resetProgress(self):
        coll = self.db.task
        return coll.update_many({}, {"$set": {'progress': 0}})


if __name__ == '__main__':
    dbo=daoNodeManager()
    dbo.resetZmap()
    dbo.resetNeedToSync()
    