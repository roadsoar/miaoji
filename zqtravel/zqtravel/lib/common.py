# -*- coding: utf-8 -*-

import re
import os
import datetime

import manufacture


def remove_str(s_str, mj_re='[\n\r]'):
  mjRE = re.compile(mj_re)
  parsed_str = mjRE.sub('',s_str)
  return parsed_str

def today_str():
  return datetime.date.today().strftime('%Y%m%d')

def get_dir_name_from_spider_item(item, spider):
  '''由spider.name和file_num构成文件名，存放在/path/to/item[scenicspot_locus]/item[scenicspot_name]'''
     
  dict_item = dict(item)
  mj_cf = manufacture.ConfigMiaoJI("./spider_settings.cfg")
  data_root_dir = mj_cf.get_str('global','spider_data_dir')
  dir1 = dict_item.get("scenicspot_locus")
  dir2 = dict_item.get("scenicspot_name")
  if 'scenicspot_province' in dict_item:
     dir1 = dict_item.get("scenicspot_province")
     dir2 = dict_item.get("scenicspot_locus")
  file_path = os.path.join(data_root_dir, dir1, dir2)
  
  if not os.path.isdir(file_path):
    os.makedirs(file_path)
  
  #file_name = "_".join([spider.name, today_str(), str(file_num)]) + ".json"
  #absolute_path_file = os.path.join(file_path, file_name)
  
  return file_path
