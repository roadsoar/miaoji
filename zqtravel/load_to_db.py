#!/bin/env python

# -*- coding: utf-8 -*-

from zqtravel.lib.mysql import LoadToMysql
from zqtravel.lib.manufacture import ConfigMiaoJI

mj_cf = ConfigMiaoJI("zqtravel/db_settings.cfg")


if __name__ == '__main__':

   host = mj_cf.get_str('global','host')
   port = mj_cf.get_str('global','port')
   db_user = mj_cf.get_str('global','db_user')
   db_passwd = mj_cf.get_str('global','db_passwd')
   db_name = mj_cf.get_str('global','db_name')

   mysql_db = LoadToMysql(database='zqtravel')
   mysql_db.connect_mysql()
   country_no_list = mysql_db.selectall('select * from Country');
   for row in country_no_list:
      print "%s,%s,%s,%s" % (str(row[0]),row[1],row[2],str(row[3]))
   mysql_db.close()
