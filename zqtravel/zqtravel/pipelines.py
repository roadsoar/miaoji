# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sys, os
import json
import codecs
import random
from scrapy import log
from scrapy.exceptions import DropItem

from zqtravel.lib.common import get_dir_name_from_spider_item, today_str


class TravelPipeline(object):
  def __init__(self):
    self.travel_file = None

  def process_item(self, item, spider):
    self.open_file(item, spider)
    dict_item = dict(item)
    line = json.dumps(dict_item) + "\n"
    try:
        if dict_item.get('travels_content'):
           self.travel_file.write(line.decode('unicode_escape'))
           return item
        else:
           return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)

  def open_file(self, item, spider):
    file_path = get_dir_name_from_spider_item(item, spider)
    # 保存游记的文件
    travel_file = "_".join([spider.name, today_str(), str(random.randint(1,sys.maxint))]) + ".json"

    path_travel_file = os.path.join(file_path, travel_file)

    try:
      self.travel_file = codecs.open(path_travel_file, 'w', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + file_name, level=log.ERROR)
    finally:
      pass

  def spider_closed(self, spider):  
    if not self.file:
       self.travel_file.close()


class ScenicspotPipeline(object):
  def __init__(self):
    self.scenicspot_file = None

  def process_item(self, item, spider):
    self.open_file(item, spider)
    dict_item = dict(item)
    line = json.dumps(dict_item) + "\n"
    try:
        if dict_item.get('scenicspot_intro'):
           self.scenicspot_file.write(line.decode('unicode_escape'))
           return item
        else:
           return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)

  def open_file(self, item, spider):
    file_path = get_dir_name_from_spider_item(item, spider)
    # 保存景点信息的文件
    scenicspot_info_file = "scenicspot_info.txt"

    path_scenicspot_info_file = os.path.join(file_path, scenicspot_info_file)

    try:
      self.scenicspot_file = codecs.open(path_scenicspot_info_file, 'w', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + file_name, level=log.ERROR)
    finally:
      pass

  def spider_closed(self, spider):  
    if not self.file:
       self.scenicspot_file.close() 
