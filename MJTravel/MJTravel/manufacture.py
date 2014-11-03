# -*- encoding: utf-8 -*-

import ConfigParser
from MJTravel.lib.common import remove_str

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

  def set(self, field, key, value):
     try:
       self.cfMJ.set(field, key, value)
       self.cfMJ.write(open(self.path, "w"))
     except:
       return False
     return True

