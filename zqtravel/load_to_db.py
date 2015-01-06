
# -*- coding: utf-8 -*-

from zqtravel.lib.mysql import LoadToMysql
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import str_count_inside, max_id_from_db, dict_data_from_db

import os
import glob

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

def get_info_from(db_obj, sql):
   connected_obj = db_obj
   src_data = connected_obj.selectall(sql)
   dict_data = dict_data_from_db(src_data)
   return dict_data

def load_data_to_db():
   db_obj = connect_mysql()
   data_root_dir = mj_cf.get_str('global','data_root_dir')
   start_count = str_count_inside(data_root_dir, '/')
   
   for root, dirs, files in os.walk(data_root_dir):  
      root_count = str_count_inside(root, '/')
      num = root_count - start_count
      # Load the provinces into database
      if num == 0:
         country_query_sql = 'select Country_name, Country_no from Country'
         country_name_to_id = get_info_from(db_obj, country_query_sql)
         for province_name in dirs:
             country_no = country_name_to_id[u'中国']
             province_query_sql = 'select Province_name, Province_no from Province'
             province_name_to_id = get_info_from(db_obj, province_query_sql)
             province_ids_sql = 'select Province_no from Province'
             max_id = get_max_id(db_obj, province_ids_sql)
             if max_id == -1:
                max_id = 1000
             else:
                max_id += 1
             province_file = os.path.join(root, province_name, province_name + '_txt')
             if os.path.isfile(province_file):
                for line in open(province_file):
                    province_info = eval(line)
                    province_intrd = province_info['scenicspot_intro']
             else:
               province_intrd = ''

             if province_name.decode('utf-8') not in province_name_to_id.keys():
                insert_province_sql = 'insert into Province(Province_no, Province_name, Province_intrd, Country_no) values(%d, "%s", "%s", %d)' % (max_id, province_name,province_intrd,country_no)
                db_obj.insertone(insert_province_sql)
                db_obj.commit()
      # Load the Cities into the database 
      elif num == 1:
         province_query_sql = 'select Province_name, Province_no from Province'
         province_name_to_id = get_info_from(db_obj, province_query_sql)
         for city_name in dirs:
             starti = root.rfind('/')
             province_name = root[starti+1:]
             province_no = province_name_to_id[province_name.decode('utf-8')]
             city_query_sql = 'select City_name, City_no from City'
             city_name_to_id = get_info_from(db_obj, city_query_sql)
             city_ids_sql = 'select City_no from City'
             max_id = get_max_id(db_obj, city_ids_sql)
             if max_id == -1:
                max_id = 10000
             else:
                max_id += 1

             city_file = os.path.join(root, city_name, city_name + '_txt')
             if os.path.isfile(city_file):
                for line in open(city_file):
                    city_info = eval(line)
                    city_intrd = city_info['scenicspot_intro']
             else:
               city_intrd = ''

             if city_name.decode('utf-8') not in city_name_to_id.keys():
                insert_city_sql = 'insert into City(City_no, City_name, City_intrd, Province_no) values(%d, "%s", "%s", %d)' % (max_id, city_name,city_intrd,province_no)
                db_obj.insertone(insert_city_sql)
                db_obj.commit()

      # Load the scenicspots into the databases
      elif num == 2:
         city_query_sql = 'select City_name, City_no from City'
         city_name_to_id = get_info_from(db_obj, city_query_sql)
         for scenicspot_name in dirs:
             starti = root.rfind('/')
             city_name = root[starti+1:]
             city_no = city_name_to_id[city_name.decode('utf-8')]
             scenicspot_query_sql = 'select Scenicspot_name, City_no from Scenicspot'
             scenicspot_name_to_city_id = get_info_from(db_obj, scenicspot_query_sql)
             scenicspot_ids_sql = 'select Scenicspot_no from Scenicspot'
             max_id = get_max_id(db_obj, scenicspot_ids_sql)
             if max_id == -1:
                max_id = 100000
             else:
                max_id += 1

             scenicspot_file = r'/'.join([root, scenicspot_name, '[0-9]*_txt'])
             scenicspot_file_list = glob.glob(scenicspot_file)
             null = "" # define this variable for below syntax: scenicspot_info = eval(line)
             for txt_file in scenicspot_file_list:
                 file_size = os.path.getsize(txt_file)
                 # read the text file which is not empty
                 if file_size > 3:
                    for line in open(txt_file):
                        scenicspot_info = eval(line)
                        scenicspot_intrd = scenicspot_info.get('scenicspot_intro','')
                        scenicspot_level = float(scenicspot_info.get('scenicspot_grade',0))
                        scenicspot_address = scenicspot_info.get('scenicspot_address','')
                        scenicspot_telephone = scenicspot_info.get('scenicspot_tel','')
                        scenicspot_web = scenicspot_info.get('scenicspot_webaddress','')
                        scenicspot_heat = int(scenicspot_info.get('helpful_num',0))
                        scenicspot_ticketprice = scenicspot_info.get('scenicspot_ticket',0) # contain the unit of money, like $, so the price is string type
                        all_scenicspot_name = scenicspot_name_to_city_id.keys()
                        if scenicspot_name.decode('utf-8') not in all_scenicspot_name: #or\
#                           scenicspot_name.decode('utf-8') in all_scenicspot_name and city_no != scenicspot_name_to_city_id.get(scenicspot_name.decode('utf-8'), -1):
                           insert_scenicspot_sql = 'insert into Scenicspot(Scenicspot_no, Scenicspot_name, Scenicspot_intrd, Scenicspot_level, Scenicspot_address,\
                                                                           Scenicspot_telephone, Scenicspot_web, Scenicspot_heat, Scenicspot_ticketprice, City_no)\
                                                                    values(%d, "%s", "%s", %f, "%s", "%s", "%s", %d, "%s", %d)'\
                                                   % (max_id, scenicspot_name,scenicspot_intrd, scenicspot_level, scenicspot_address, scenicspot_telephone, scenicspot_web, scenicspot_heat, scenicspot_ticketprice, city_no)
                           db_obj.insertone(insert_scenicspot_sql)
                           db_obj.commit()

if __name__ == '__main__':

   print "Start loading..."
   load_data_to_db()
   print "Finished for loading data into database."
