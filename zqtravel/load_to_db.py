# -*- coding: utf-8 -*-

from zqtravel.lib.mysql import LoadToMysql
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import str_count_inside, max_id_from_db, dict_data_from_db

import os, re
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

def get_value_for(key, source_str):
   key_str = '.*"' + key + '":\s*"(.*?)"'
   matched_key = re.match(key_str, source_str)
   if matched_key:
      return matched_key.group(1)
   else:
      return ''

def load_data_to_db():
   db_obj = connect_mysql()
   data_root_dir = mj_cf.get_str('global','data_root_dir')
   start_count = str_count_inside(data_root_dir, '/') # 用数字来区分省、市/县、景点
   null = "" # define this variable for below syntax: scenicspot_info = eval(line)

   invalid_file = open('./invalid_files.txt', 'a+')

   for root, dirs, files in os.walk(data_root_dir):  
      root_count = str_count_inside(root, '/') # 用数字来区分省、市/县、景点
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
             try:
               if os.path.isfile(province_file):
                  fl = open(province_file,"r")
                  lines = fl.readlines()
                  fl.close()
                  lines_str = ''.join(lines).strip()
                  try:
                     province_info = eval(lines_str)
                     province_intrd = province_info['scenicspot_intro']
                     province_traveling_time = province_info['best_traveling_time']
                     province_history = province_info['history']
                     province_custom = province_info['custom']
                     province_culture = province_info['culture']
                     province_weather = province_info['weather']
                     province_days = province_info['num_days']
                     province_dressing = province_info['scenicspot_dressing']
                     province_language = province_info['language']
                  except Exception:
                     province_intrd = get_value_for('scenicspot_intro', lines_str)
                     province_traveling_time = get_value_for('best_traveling_time', lines_str)
                     province_history = get_value_for('history', lines_str)
                     province_custom = get_value_for('custom', lines_str)
                     province_culture = get_value_for('culture', lines_str)
                     province_weather = get_value_for('weather', lines_str)
                     province_days = get_value_for('num_days', lines_str)
                     province_dressing = get_value_for('scenicspot_dressing', lines_str)
                     province_language = get_value_for('language', lines_str)
               else:
                 province_intrd = ''
                 province_traveling_time = ''
                 province_history = ''
                 province_custom  = ''
                 province_culture = ''
                 province_weather = ''
                 province_days = ''
                 province_dressing = ''
                 province_language = ''
  
               if province_name.decode('utf-8') not in province_name_to_id.keys():
                  insert_province_sql = 'insert into Province(Province_no, Province_name, Province_intrd, Country_no, Province_traveling_time, Province_dressing, Province_custom, Province_culture, Province_history, Province_weather, Province_days, Province_language) values(%d, "%s", "%s", %d, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (max_id, province_name,province_intrd,country_no,province_traveling_time,province_dressing,province_custom,province_culture,province_history,province_weather,province_days,province_language)
                  db_obj.insertone(insert_province_sql)
                  db_obj.commit()
             except Exception , msg:
               invalid_file.write(province_file + str(msg) + '\n')
               invalid_file.flush()
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
             try:
               if os.path.isfile(city_file):
                  fl = open(city_file)
                  lines = fl.readlines()
                  fl.close()
                  lines_str = ''.join(lines).strip()
                  try:
                     city_info = eval(lines_str)
                     city_intrd = city_info['scenicspot_intro']
                     city_traveling_time = city_info['best_traveling_time']
                     city_history = city_info['history']
                     city_custom = city_info['custom']
                     city_culture = city_info['culture']
                     city_weather = city_info['weather']
                     city_days = city_info['num_days']
                     city_dressing = city_info['scenicspot_dressing']
                     city_language = city_info['language']
                  except Exception:
                     city_intrd = get_value_for('scenicspot_intro', lines_str)
                     city_traveling_time = get_value_for('best_traveling_time', lines_str)
                     city_history = get_value_for('history', lines_str)
                     city_custom = get_value_for('custom', lines_str)
                     city_culture = get_value_for('culture', lines_str)
                     city_weather = get_value_for('weather', lines_str)
                     city_days = get_value_for('num_days', lines_str)
                     city_dressing = get_value_for('scenicspot_dressing', lines_str)
                     city_language = get_value_for('language', lines_str)
               else:
                 city_intrd = ''
                 city_traveling_time = ''
                 city_history = ''
                 city_custom  = ''
                 city_culture = ''
                 city_weather = ''
                 city_days = ''
                 city_dressing = ''
                 city_language = ''
             except Exception , msg:
               invalid_file.write(city_file + str(msg) + '\n')
               invalid_file.flush()
               city_intrd = ''
               city_traveling_time = ''
               city_history = ''
               city_custom  = ''
               city_culture = ''
               city_weather = ''
               city_days = ''
               city_dressing = ''
               city_language = '' 
             finally:
               if city_name.decode('utf-8') not in city_name_to_id.keys():
                  insert_city_sql = 'insert into City(City_no, City_name, City_intrd, Province_no, City_best_traveling_time, City_dressing, City_custom, City_culture, City_history, City_weather, City_days, City_language) values(%d, "%s", "%s", %d, "%s", "%s","%s","%s","%s","%s","%s","%s")' % (max_id, city_name,city_intrd,province_no,city_traveling_time,city_dressing,city_custom,city_culture,city_history,city_weather,city_days,city_language)
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
             for txt_file in scenicspot_file_list:
                 file_size = os.path.getsize(txt_file)
                 # read the text file which is not empty
                 if file_size > 3:
                    #for line in open(txt_file):
                      try:
                        fl = open(txt_file)
                        lines = fl.readlines()
                        fl.close()
                        lines_str = ''.join(lines).strip()
                        try:
                           scenicspot_info = eval(lines_str)
                           scenicspot_intrd = scenicspot_info.get('scenicspot_intro','')
                           scenicspot_level = float(scenicspot_info.get('scenicspot_grade',0))
                           scenicspot_address = scenicspot_info.get('scenicspot_address','')
                           scenicspot_telephone = scenicspot_info.get('scenicspot_tel','')
                           scenicspot_web = scenicspot_info.get('scenicspot_webaddress','')
                           scenicspot_heat = int(scenicspot_info.get('helpful_num',0))
                           scenicspot_ticketprice = scenicspot_info.get('scenicspot_ticket','') # contain the unit of money, like $
                           scenicspot_comments = scenicspot_info.get('scenicspot_comments','')
                           scenicspot_impression = scenicspot_info.get('scenicspot_impression','')
                           scenicspot_opentime = scenicspot_info.get('scenicspot_opentime','')
                           scenicspot_usetime = scenicspot_info.get('scenicspot_usetime','')
                           scenicspot_traffic = scenicspot_info.get('traffic','')
                        except Exception:
                           scenicspot_intrd = get_value_for('scenicspot_intro', lines_str)
                           scenicspot_level = float(get_value_for('scenicspot_grade', lines_str))\
                                       if len(get_value_for('scenicspot_grade', lines_str)) > 0 else 0
                           scenicspot_address = get_value_for('scenicspot_address', lines_str)
                           scenicspot_telephone = get_value_for('scenicspot_tel', lines_str)
                           scenicspot_web = get_value_for('scenicspot_webaddress', lines_str)
                           scenicspot_heat = int(get_value_for('helpful_num', lines_str))\
                                      if len(get_value_for('helpful_num', lines_str)) > 0 else 0
                           scenicspot_ticketprice = get_value_for('scenicspot_ticket', lines_str)
                           scenicspot_comments = get_value_for('scenicspot_comments', lines_str)
                           scenicspot_impression = get_value_for('scenicspot_impression', lines_str)
                           scenicspot_opentime = get_value_for('scenicspot_opentime', lines_str)
                           scenicspot_usetime = get_value_for('scenicspot_usetime', lines_str)
                           scenicspot_traffic = get_value_for('traffic', lines_str)

                        all_scenicspot_name = scenicspot_name_to_city_id.keys()
                        if scenicspot_name.decode('utf-8') not in all_scenicspot_name: #or\
#                           scenicspot_name.decode('utf-8') in all_scenicspot_name and city_no != scenicspot_name_to_city_id.get(scenicspot_name.decode('utf-8'), -1):
                           insert_scenicspot_sql = 'insert into Scenicspot(Scenicspot_no, Scenicspot_name, Scenicspot_intrd, Scenicspot_level, Scenicspot_address, Scenicspot_telephone, Scenicspot_web, Scenicspot_heat, Scenicspot_ticketprice, City_no, Scenicspot_opentime, Scenicspot_usetime, Scenicspot_comments, Scenicspot_impression, Scenicspot_traffic) \
                                             values(%d, "%s", "%s", %f, "%s", "%s", "%s", %d, "%s", %d, "%s", "%s", "%s", "%s", "%s")'\
                 %(max_id, scenicspot_name,scenicspot_intrd, scenicspot_level, scenicspot_address, scenicspot_telephone, scenicspot_web, scenicspot_heat, scenicspot_ticketprice, city_no, scenicspot_opentime, scenicspot_usetime, scenicspot_comments, scenicspot_impression, scenicspot_traffic)
                           db_obj.insertone(insert_scenicspot_sql)
                           db_obj.commit()
                      except Exception , msg:
                        invalid_file.write(txt_file + str(msg) +'\n')
                        invalid_file.flush()

if __name__ == '__main__':

   print "Start loading..."
   load_data_to_db()
   print "Finished for loading data into database."
