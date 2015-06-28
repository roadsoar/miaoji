# -*- encoding: utf-8 -*-

import ConfigParser

class ConfigMiaoJI:
  def __init__(self,config_path):
    self.path = config_path
    self.cfMJ = ConfigParser.ConfigParser()
    self.cfMJ.read(self.path)

  def get_dict(self, field, key):
      dict_str = self.cfMJ.get(field, key)
      return eval(dict_str)

  def get_list(self, field, key):
      try:
         list_str = self.cfMJ.get(field, key)
         return eval(list_str)
      except:
         return None

  def get_str(self, field, key):
      field_value = ''.join(self.cfMJ.get(field, key))
      return field_value

  def get_int(self, field, key):
      field_value = self.cfMJ.get(field, key)
      return int(field_value)

  def get_bool(self, field, key):
      field_value = self.cfMJ.get(field, key)
      return eval(field_value)

  def get_float(self, field, key):
      field_value = self.cfMJ.get(field, key)
      return float(field_value)

  def set(self, field, key, value):
     try:
       self.cfMJ.set(field, key, value)
       self.cfMJ.write(open(self.path, "w"))
     except:
       return False
     return True

