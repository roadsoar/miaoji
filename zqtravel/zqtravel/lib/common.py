# -*- coding: utf-8 -*-

import re
import os
import datetime

import manufacture

'''通用函数'''

def remove_str(s_str, mj_re='[\n\r]'):
  mjRE = re.compile(mj_re)
  parsed_str = mjRE.sub('',s_str)
  return parsed_str

def today_str():
  return datetime.date.today().strftime('%Y%m%d')

def get_data_dir_with(subdir=""):
  
  sub_dir = subdir
  if type(subdir) is list:
    sub_dir = '/'.join(subdir)

  mj_cf = manufacture.ConfigMiaoJI("./spider_settings.cfg")
  data_root_dir = mj_cf.get_str('global','travel_urls_dir')
  
  pre_dir = os.path.join(data_root_dir, sub_dir)
  if not os.path.isdir(pre_dir):
    os.makedirs(pre_dir)
  return pre_dir

def get_dir_name_from_spider_item(item, spider):
  ''''''
     
  dict_item = dict(item)
  mj_cf = manufacture.ConfigMiaoJI("./spider_settings.cfg")
  data_root_dir = mj_cf.get_str('global','spider_data_dir')
  file_path = data_root_dir

  dir1 = dict_item.get("scenicspot_province")
  dir2 = dict_item.get("scenicspot_locus")
  dir3 = dict_item.get("scenicspot_name")
  if '' == dir2 or dir2 == dir3:
     dir3 = ''

  if spider:
     file_path = os.path.join(data_root_dir,spider.name, dir1, dir2, dir3)
     if not os.path.isdir(file_path):
        os.makedirs(file_path)
  else:
     file_path = '/'.join([dir1, dir2, dir3])
  
  return file_path

def mkdirs(file_path):
    if not os.path.exists(file_path):
       os.makedirs(file_path)

def get_dir_with_province_name(item, spider):
  ''''''

  dict_item = dict(item)
  mj_cf = manufacture.ConfigMiaoJI("./spider_settings.cfg")
  data_root_dir = mj_cf.get_str('global','spider_data_dir')
  file_path = data_root_dir

  dir1 = dict_item.get("scenicspot_province")

  file_path = os.path.join(data_root_dir,spider.name, dir1)

  if not os.path.isdir(file_path):
     os.makedirs(file_path)

  return file_path


def str_count_inside(src_string, aString):
  count = len(src_string.split(aString)) - 1
  return count

def max_id_from_db(id_results):
   if not id_results:
      return -1

   max_id = max(id_results)
   return max_id[0]

def dict_data_from_db(data):
   if not data:
      return {}

   return dict(data)
