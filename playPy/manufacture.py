#!/usr/bin/env python

import ConfigParser

class ConfigMiaoJI:
  def __init__(self,config_path):
    self.path = config_path
    self.cfMJ = ConfigParser.ConfigParser()
    self.cfMJ.read(self.path)

  def get(self, field, key):
    rs = ""
    try:
      rs = self.cfMJ.get(field, key)
    except: 
      rs = ""
    return rs

  def set(self, field, key, value):
     try:
       self.cfMJ.set(field, key, value)
       self.cfMJ.write(open(self.path, "w"))
     except:
       return False
     return True


if __name__ == "__main__":
  mj_cf = ConfigMiaoJI("./manufacture.cfg")
  print("file threads used: %d" % int(mj_cf.get("global","process_file_threads")))
  print("xiecheng travelogue name: %s" % mj_cf.get("xiecheng_travelogue","name"))
  print("xiecheng travelogue file path: %s" % mj_cf.get("xiecheng_travelogue","file_path"))
 
  if mj_cf.set("xiecheng_travelogue","test_key1","tval1"):
     print "set successfully"
