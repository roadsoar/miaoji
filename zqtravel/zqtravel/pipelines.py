# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sys
import json
import codecs
from scrapy import log

from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, today_str

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class JsonPipeline(object):
  def __init__(self):
    self.file_num = 1
    self.file = None

  def process_item(self, item, spider):
    self.open_file(self.file_num, spider)
    dict_item = dict(item)
    line = json.dumps(dict_item) + "\n"
    try:
        self.file.write(line.decode('unicode_escape'))
    except Exception ,e:
        log.msg('Failed to write travel records to file', level=log.ERROR)
    self.file_num += 1
    return item

  def open_file(self, file_num, spider):
    data_dir = mj_cf.get_str('global','spider_data_dir')
    file_name = data_dir + "_".join([spider.name, today_str(), str(file_num)]) + ".json"
    try:
      self.file = codecs.open(file_name, 'w', encoding='utf-8')
    except Exception, e:
      log.msg('Failed to open file: ' + file_name, level=log.ERROR)
    finally:
      pass

  def spider_closed(self, spider):  
    if not self.file:
        self.file.close()
