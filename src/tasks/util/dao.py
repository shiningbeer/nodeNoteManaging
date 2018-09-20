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
        self.db = self.client.node
    def update(self,col,find_dict,update_dict):
        coll=self.db[col]
        return coll.update_many(find_dict, {"$set":update_dict })

    def findOne(self,col,find_dict):
        coll=self.db[col]
        return coll.find_one(find_dict)

    def insert(self,tableName,document):
        coll=self.db[tableName]
        coll.insert_one(document)

    def saveResult(self,tableName,document):
        coll=self.db[tableName]
        coll.insert_one(document)


if __name__ == '__main__':
    dbo=daoNodeManager()
    dbo.insert('task',{'plugin':{'name':'s7.py'},'ipRange':['210.203.0.1','202,21.1.1'],'paused':False,'complete':False,'goWrong':False,'running':False,'progress':0,'type':'plugin'})
