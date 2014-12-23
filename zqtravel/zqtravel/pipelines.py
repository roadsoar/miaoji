# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sys, os
import json
import codecs
import random

from zqtravel.lib.common import get_dir_name_from_spider_item, today_str, mkdirs, get_dir_with_province_name

from scrapy import log
from scrapy.http import Request
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

    def file_path(self, request, response=None, info=None):
        if not isinstance(request, Request):
           _warn()
           url = request
        else:
           url = request.url

        meta = response.meta
        scenicspot_province = meta.get('scenicspot_province', '')
        scenicspot_locus = meta.get('scenicspot_locus', '')
        scenicspot_name = meta.get('scenicspot_name', '')

        image_name = url.split('/')[-1]
        log.msg('========================'+'/'.join([scenicspot_province, scenicspot_locus, scenicspot_name, 'scenicspot_image', image_guid]))
        return '/'.join([scenicspot_province, scenicspot_locus, scenicspot_name, 'scenicspot_image', image_name])

    def get_media_requests(self, item, info):
         scenicspot_province = item['scenicspot_province']
         scenicspot_locus = item['scenicspot_locus']
         scenicspot_name = item['scenicspot_name']
         for url in item.get('image_urls', []):
            yield Request(url, meta={'scenicspot_province':scenicspot_province, 'scenicspot_locus':scenicspot_locus, 'scenicspot_name':scenicspot_name})

   # def item_completed(self, results, item, info):
#        if 'images' in item.fields:
      #  item['images'] = [x for ok, x in results if ok]
      #  return item

#        image_pre_dir = get_dir_name_from_spider_item(item, None)
#        from scrapy.conf import settings
#        store_uri = settings['IMAGES_STORE']
#        mkdirs(store_uri + image_pre_dir)
# 
#        dict_item = dict(item)
#        travel_id = ''
#        if 'travels_link' in item.fields:
#           link = dict_item.get('travels_link')
#           travel_id = link[link.rfind('/')+1:-5]
#
#        if 'images' in item.fields:
#            images = [x for ok, x in results if ok]
#            item['images'] = []
#            if images:
#               for image in images:
#                   tmp_path = image.get('path').split('/')
#                   image_file_name = '.'.join([travel_id, tmp_path[1]])
#                   path = '/'.join([image_pre_dir, tmp_path[0], image_file_name])
#                   image['path'] = path
#                   item['images'].append(image)
#
#        return item

class TravelLinkPipeline(object):
  def __init__(self):
    self.travel_link_file = None

  def process_item(self, item, spider):
    try:
      if item:
        self.open_file(item, spider)
        dict_item = dict(item)
        line = json.dumps(dict_item) + "\n"
        if dict_item.get('travels_link'):
           self.travel_link_file.write(line.decode('unicode_escape'))
        else:
           return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)

  def open_file(self, item, spider):
    file_path = get_dir_with_province_name(item, spider)
    # 保存游记连接
    link_file = "travel_link.txt"

    path_link_file = os.path.join(file_path, link_file)

    try:
      self.travel_link_file = codecs.open(path_link_file, 'aw', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + path_link_file, level=log.ERROR)
    finally:
      pass

