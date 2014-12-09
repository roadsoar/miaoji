# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sys, os
import json
import codecs
import random

from zqtravel.lib.common import get_dir_name_from_spider_item, today_str

from scrapy import log
from scrapy.exceptions import DropItem
from scrapy.contrib.pipeline.images import ImagesPipeline


class TravelPipeline(object):
  def __init__(self):
    self.travel_file = None

  def process_item(self, item, spider):
    try:
      if item:
        self.open_file(item, spider)
        dict_item = dict(item)
        line = json.dumps(dict_item) + "\n"
        if dict_item.get('travels_content'):
           self.travel_file.write(line.decode('unicode_escape'))
        else:
           return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)

  def open_file(self, item, spider):
    file_path = get_dir_name_from_spider_item(item, spider)
    # 保存游记的文件
    dict_item = dict(item)
    link = dict_item.get('travels_link')
    link_id = link[link.rfind('/')+1:-5]
    travel_file = "_".join([dict_item.get('travels_praisenum'),dict_item.get('travels_viewnum'), dict_item.get('travels_commentnum'), link_id, 'json'])

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
    try:
        if item:
          self.open_file(item, spider)
          dict_item = dict(item)
          line = json.dumps(dict_item) + "\n"
          if 'scenicspot_intro' in dict_item:
             self.scenicspot_file.write(line.decode('unicode_escape'))
          else:
             return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)

  def open_file(self, item, spider):
    file_path = get_dir_name_from_spider_item(item, spider)
    # 保存景点信息的文件
    dict_item = dict(item)
    if 'scenicspot_grade' in dict_item:
        scenicspot_grade = dict_item.get('scenicspot_grade')
        scenicspot_info_file = '_'.join([scenicspot_grade, dict_item.get('scenicspot_name'), 'txt'])
    else:
        scenicspot_info_file = '_'.join([dict_item.get('scenicspot_name'), 'txt'])

    path_scenicspot_info_file = os.path.join(file_path, scenicspot_info_file)

    try:
      self.scenicspot_file = codecs.open(path_scenicspot_info_file, 'w', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + file_name, level=log.ERROR)
    finally:
      pass

  def spider_closed(self, spider):  
    if not self.file:
      # self.scenicspot_file.close() 
      pass


class ImagesStorePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item

