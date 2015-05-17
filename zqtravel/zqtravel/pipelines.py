# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sys, os
import json
import codecs
import random
import hashlib

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
        # 删除images和images_urls字段，因为游记分析不需要且占很多空间
        if 'image_urls' in dict_item.keys():
           dict_item.pop('image_urls')
        if 'images' in dict_item.keys():
           dict_item.pop('images')

        line = json.dumps(dict_item)
        if dict_item.get('travel_content'):
           self.travel_file.write(line.decode('unicode_escape'))
        else:
           return item
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)

  def open_file(self, item, spider):
    file_path = get_dir_name_from_spider_item(item, spider)#.decode('utf-8')
    # 保存游记的文件
    dict_item = dict(item)
    link = dict_item.get('travel_link')
    link_id = link[link.rfind('/')+1:-5]
    travel_file = "_".join([dict_item.get('travel_praisenum'),dict_item.get('travel_viewnum'), dict_item.get('travel_commentnum'), link_id, 'json'])

    path_travel_file = os.path.join(file_path, travel_file)

    try:
      self.travel_file = codecs.open(path_travel_file, 'w', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + path_travel_file, level=log.ERROR)
    finally:
      pass


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
        log.msg('Failed to write scenicspot information to file', level=log.ERROR)

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
         '''重写scrapy的默认函数，以便自定义存储路径'''

         # 调试scrapy重写的函数时特别注意，如果有异常，如语法错误：NoneType调用了get()方法，使用未声明的变量等,
         # 这时是不会有错误提示输出的，给调试带来一定的迷惑性，不留神，会认为该方法没被调用，而实际是简单的语法错误.^^
         if not isinstance(request, Request):
            _warn()
            url = request
         else:
            url = request.url

         meta = request.meta
         scenicspot_province = meta.get('scenicspot_province', '')
         scenicspot_locus = meta.get('scenicspot_locus', '')
         scenicspot_name = meta.get('scenicspot_name', '')
         link_id = meta.get('link_id', '')
         image_guid = hashlib.sha1(url).hexdigest()

         image_post_dir = '%s/%s/%s/%s/%s' % (scenicspot_province, scenicspot_locus, scenicspot_name, 'images', link_id)
         image_name = '%s%s' % (image_guid, '.jpg')

         return '/'.join([image_post_dir, image_name])

    def get_media_requests(self, item, info):
         '''重写scrapy的默认函数，以传递自定义存储路径所需要的信息，如：省、市/县、景点名称'''

         scenicspot_province = item.get('scenicspot_province','')
         scenicspot_locus = item.get('scenicspot_locus','')
         scenicspot_name = item.get('scenicspot_name','')
         link = item.get('travel_link','')
         if '.html' in link:
            link_id = link[link.rfind('/')+1:-5]
         else:
            link_id = link[link.rfind('/')+1:]

         return [Request(x, \
                        meta={'scenicspot_province':scenicspot_province, \
                              'scenicspot_locus':scenicspot_locus, \
                              'scenicspot_name':scenicspot_name, \
                              'link_id':link_id, \
                             }\
                        ) for x in item.get('image_urls', []) \
                ]

class TravelLinkPipeline(object):
  def __init__(self):
    self.travel_link_file = None

  def process_item(self, item, spider):
    try:
      if item:
        self.open_file(item, spider)
        dict_item = dict(item)
        line = json.dumps(dict_item) + "\n"
        if dict_item.get('travel_link'):
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

