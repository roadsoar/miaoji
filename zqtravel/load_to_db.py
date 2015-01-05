#!/bin/env python

# -*- coding: utf-8 -*-

from zqtravel.lib.mysql import LoadToMysql
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import str_count_inside, max_id_from_db

import os

mj_cf = ConfigMiaoJI("zqtravel/db_settings.cfg")

def connect_mysql():
   host = mj_cf.get_str('global','host')
   port = mj_cf.get_int('global','port')
   db_user = mj_cf.get_str('global','db_user')
   db_passwd = mj_cf.get_str('global','db_passwd')
   db_name = mj_cf.get_str('global','db_name')

   mysql_db = LoadToMysql(host=host, port=port, user=db_user, passwd=db_passwd, database=db_name)
   mysql_db.connect()
   return mysql_db

def get_max_id(db_obj, sql):
   connected_obj = db_obj
   ids_list = connected_obj.selectall(sql)
   return max_id_from_db(ids_list)

def load_data_to_db():
   data_root_dir = mj_cf.get_str('global','data_root_dir')
   for root, dirs, files in os.walk(data_root_dir):  
      print os.path.join(root)

if __name__ == '__main__':

   db_obj = connect_mysql()
   ids_sql = 'select Province_no from Province'
   max_id = get_max_id(db_obj, ids_sql)
   print max_id
   load_data_to_db()
   db_obj.close()
