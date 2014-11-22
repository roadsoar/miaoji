# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sys, os
import json
import codecs
from scrapy import log
from scrapy.exceptions import DropItem

#from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import get_dir_name_from_spider_item, today_str

#mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class JsonPipeline(object):
  def __init__(self):
    self.file_num = 1
    self.travel_file = None
    self.scenicspot_file = None

  def process_item(self, item, spider):
    self.open_file(self.file_num, item, spider)
    dict_item = dict(item)
    line = json.dumps(dict_item) + "\n"
    try:
        if dict_item.get('scenicspot_intro') and not os.path.isfile(self.scenicspot_file):
           self.scenicspot_file.write(line.decode('unicode_escape'))
           self.file_num += 1
           return item
        #else:
        #   raise DropItem()
        else:
           self.travel_file.write(line.decode('unicode_escape'))
           self.file_num += 1
           return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)
    self.file_num += 1
    return item

  def open_file(self, file_num, item, spider):
    file_path = get_dir_name_from_spider_item(item, spider)
    # 保存游记的文件
    travel_file = "_".join([spider.name, today_str(), str(file_num)]) + ".json"
    # 保存景点信息的文件
    scenicspot_info_file = "scenicspot_info.txt"

    path_travel_file = os.path.join(file_path, travel_file)
    path_scenicspot_info_file = os.path.join(file_path, scenicspot_info_file)

    try:
      self.travel_file = codecs.open(path_travel_file, 'w', encoding='utf-8')
      self.scenicspot_file = codecs.open(path_scenicspot_info_file, 'w', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + file_name, level=log.ERROR)
    finally:
      pass

  def spider_closed(self, spider):  
    if not self.file:
       self.travel_file.close()
       self.scenicspot_file.close() 
