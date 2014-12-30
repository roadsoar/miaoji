# -*- coding: utf-8 -*-

from zqtravel.lib.mysql import LoadToMysql

mj_cf = ConfigMiaoJI("./db_settings.cfg")


if __name__ == '__main__':

   host = mj_cf.get_str('global','host')
   db_user = mj_cf.get_str('global','db_user')
   db_passwd = mj_cf.get_str('global','db_passwd')
   db_name = mj_cf.get_str('global','db_name')

   mysql_db=LoadToMysql(database='zqtravel')
   _rows = mysql_db.executeQueryAll('select userid,nick from tb_user limit 10');
   for row in _rows:
      print row
      print 'nick:%s' % str(row['nick'])
   mysql_db.close()
