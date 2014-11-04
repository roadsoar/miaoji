# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import json
import codecs
from MJTravel.lib.common import remove_str, today_str

class JsonWriterPipeline(object):
  def __init__(self):
    self.file_num = 1
  
  def process_item(self, item, spider):
    self.open_file(self.file_num, spider)
    dict_item = dict(item)
    line = json.dumps(dict_item) + "\n"
    self.file.write(line.decode('unicode_escape'))
    self.file_num += 1
    return item 

  def open_file(self, file_num, spider):
    file_name = "_".join([spider.name, today_str(), str(file_num)]) + ".json"
    try:
      self.file = codecs.open(file_name, 'w', encoding='utf-8')
    finally:
      pass
