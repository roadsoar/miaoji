# -*- coding: utf-8 -*-

#from zqtravel.lib.manufacture import ConfigMiaoJI

import os, sys, string  
import MySQLdb  
import codecs  

class LoadToMysql(object):
   def __init__(self, host='localhost', port=3306, user='root', passwd='123456', database=''):
      self.host = host
      self.db_port= port
      self.db_user = user
      self.db_passwd = passwd
      self.database= database
      self.conn = None

   # 连接数据库  
   def connect_mysql(self):
      try:  
         self.conn = MySQLdb.connect(host=self.host, user=self.db_user, passwd=self.db_passwd, db=self.database, port=self.db_port, charset='utf8')
      except Exception, e:  
         print e  
         self.close()
         sys.exit()  
    
   # 关闭数据库
   def close(self):
      if not self.conn is None:
         self.conn.close()  
  
   # 查询数据库
   def selectall(self, sql):
      cursor = self.conn.cursor()
      cursor.execute("set names 'UTF8'")  ## 设置mysql的字符编码
      cursor.execute(sql)  
      alldata = cursor.fetchall()
      cursor.close()
      return alldata

   #提交事务
   def commit(self):
      self.conn.commit()

   # 只插入一条记录
   def insertone(self, sql, isAutoCommit=False):
      cursor = self.conn.cursor()
      cursor.execute(sql)
      if isAutoCommit == True:
         self.commit()
      cursor.close()
  
   # 插入多条记录
   def insert_many(self, sql, val, isAutoCommit=False):
      cursor = self.conn.cursor()
      cursor.executemany(sql, val)
      if isAutoCommit == True:
         self.commit()
      cursor.close()

# 如果有数据返回，就循环输出, alldata是有个二维的列表  
#if alldata:  
#    for rec in alldata:  
#        print rec[0], rec[1].decode("utf-8")  
  
