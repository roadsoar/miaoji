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

  dir1 = dict_item.get("scenicspot_province", '')
  dir2 = dict_item.get("scenicspot_locus", '')
  dir3 = '' #dict_item.get("scenicspot_name", '')
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

def format_time(str_time):
    f_time = re.sub(r'[^\d :]', '/',str_time)
    num_comma = len(re.findall(':', f_time))
    if 2 == num_comma:
       return f_time
    elif 1 == num_comma:
       return '%s%s' % (f_time, ':00')
    return '%s %s' % (f_time, '00:00:00')

def a_more_than_b(left_a, right_b):
    left_v = left_a.split(u'万')[0]
    if len(left_v) == 1:
        left_v = float(left_v) 
    else:
        left_v = float(left_v) * 10000

    right_v = right_b.split(u'万')[0]
    if len(right_v) == 1:
        right_v = float(right_v)
    else:
        right_v = float(right_v) * 10000

    if left_v >= right_v:
       return True
    else:
       return False


def fetch_travel(travel_time, view_num):
    str_time = format_time(travel_time)
    date_now = datetime.datetime.now()
    date_travel = datetime.datetime.strptime(str_time, "%Y/%m/%d %X")
    interval_time = date_now - date_travel
    interval_days = interval_time.days

    mj_cf = manufacture.ConfigMiaoJI("./spider_settings.cfg")
    threshold_viewnum_in_2year = mj_cf.get_str('mafengwo_travel_spider','threshold_viewnum_in_2year')
    threshold_viewnum_in_3year = mj_cf.get_str('mafengwo_travel_spider','threshold_viewnum_in_3year')
    threshold_viewnum = mj_cf.get_str('mafengwo_travel_spider','threshold_viewnum')

    if 365 >= interval_days:
       return True
    elif 365*2 >= interval_days and a_more_than_b(view_num, threshold_viewnum_in_2year):
       return True
    elif 365*3 >= interval_days and a_more_than_b(view_num, threshold_viewnum_in_3year):
       return True
    elif a_more_than_b(view_num, threshold_viewnum):
       return True
  
    return False



def get_url_prefix(response, allowed_domains, splice_http=False):
        page_url_prefix = ''

        if not splice_http:
            for domain_name in allowed_domains:
                if domain_name in response.url:
                   page_url_prefix = 'http://' + domain_name
                   break
        else:
            for domain_name in allowed_domains:
                if domain_name in response.url:
                   page_url_prefix = 'http://www.' + domain_name
                   break
        return page_url_prefix
