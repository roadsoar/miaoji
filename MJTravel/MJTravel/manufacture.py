#!/usr/bin/env python

import ConfigParser

class ConfigMiaoJI:
  def __init__(self,config_path):
    self.path = config_path
    self.cfMJ = ConfigParser.ConfigParser()
    self.cfMJ.read(self.path)

  def get_starturls(self, field, key):
    starturls = ""
    starturls_tuple=()
    try:
     starturls = self.cfMJ.get(field, key)
     starturls_tuple = set(starturls.split(','))
    except Exception as e: 
      starturls_tuple = () 
    return starturls_tuple

  def set(self, field, key, value):
     try:
       self.cfMJ.set(field, key, value)
       self.cfMJ.write(open(self.path, "w"))
     except:
       return False
     return True

