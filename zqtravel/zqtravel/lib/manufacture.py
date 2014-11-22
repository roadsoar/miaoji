# -*- encoding: utf-8 -*-

import ConfigParser
from zqtravel.lib.common import remove_str

class ConfigMiaoJI:
  def __init__(self,config_path):
    self.path = config_path
    self.cfMJ = ConfigParser.ConfigParser()
    self.cfMJ.read(self.path)

  def get_starturls(self, field, key):
    starturls = ""
    starturls_tuple=()
    try:
     starturls = remove_str(self.cfMJ.get(field, key))
     starturls_tuple = set(eval(starturls))
    except Exception as e: 
      print e
      starturls_tuple = () 
    return starturls_tuple

  def get_allow_cities(self, field, allow_cities, disallow_cities):
      all_allow_cities = set(eval(remove_str(self.cfMJ.get(field, allow_cities))))
      all_disallow_cities = set(eval(remove_str(self.cfMJ.get(field, disallow_cities))))
      cities = all_allow_cities - all_disallow_cities

      return cities

  def get_str(self, field, key):
      field_value = ''.join(self.cfMJ.get(field, key))
      return field_value

  def set(self, field, key, value):
     try:
       self.cfMJ.set(field, key, value)
       self.cfMJ.write(open(self.path, "w"))
     except:
       return False
     return True

