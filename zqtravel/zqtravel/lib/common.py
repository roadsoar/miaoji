# -*- coding: utf-8 -*-

import re
import os
import datetime

from zqtravel.lib.manufacture import ConfigMiaoJI


def remove_str(s_str, mj_re='[\n\r]'):
  mjRE = re.compile(mj_re)
  parsed_str = mjRE.sub('',s_str)
  return parsed_str

def today_str():
  return datetime.date.today().strftime('%Y%m%d')

def get_file_name_from_spider_item(file_num, item, spider):
  '''由spider.name和file_num构成文件名，存放在/path/to/item["scenicspot_locus"]/item["scenicspot_name"]'''
     
    dict_item = dict(item)
    mj_cf = ConfigMiaoJI("../spider_settings.cfg")
    data_root_dir = mj_cf.get_str('global','spider_data_dir')
    file_path = os.path.join(data_root_dir, dict_item.get("scenicspot_locus"), dict_item.get("scenicspot_name"))
    if not os.path.isdir(file_path):
        os.path.makedirs(file_path)
    file_name = "_".join([spider.name, today_str(), str(file_num)]) + ".json"
    absolute_path_file = os.path.join(file_path, file_name)

    return bsolute_path_file
