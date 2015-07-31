# -*- coding: utf-8 -*-

import os, re, sys, signal
from lib.manufacture import ConfigMiaoJI
from lib.common_function import calcDistance
import urllib
import math
import traceback, logging
  
class Around:
  def __init__(self):
      self.around_cf = ConfigMiaoJI("./conf/route.conf")

  def get_location_from_file(self):
      str_file = self.around_cf.get_str('storage','addr_location')
      long_lat_file = open(str_file)
      lines_list = long_lat_file.readlines()
      long_lat_file.close()
      long_lat_list = [x.strip() for x in lines_list if 'NotFound' not in x]
      return long_lat_list

  def evaluate_location_around(self):
      long_lat_list = self.get_location_from_file()
      around_boundary = self.around_cf.get_int('around','around_distance')
      around_map = {}
      # 循环所有的地址
      for index, long_lat in enumerate(long_lat_list):
          longlat = long_lat.rsplit(',',2)
          location_name = longlat[0].replace('.','')
          longitude = float(longlat[1])
          latitude = float(longlat[2])
          around_map[location_name] = []
          if index % 1000 == 0:
             print index
          # 逐个比较
          for long_latB in long_lat_list[index+1:]:
              longlatB = long_latB.rsplit(',',2)
              location_nameB = longlatB[0].replace('.','')
              longitudeB = float(longlatB[1])
              latitudeB = float(longlatB[2])
              around_map[location_nameB] = []
              try:
                  distance = calcDistance(latitude, longitude, latitudeB, longitudeB)
              except Exception as e:
                  log_file = self.around_cf.get_str('logging','around_log')
                  traceback.print_exc(file=open(log_file,'w'))
                  location = '%s-%f-%f,%s-%f-%f\n' % (location_name,latitude,longitude,location_nameB,latitudeB,longitudeB)
                  self.write_to_file(log_file, location)
              if around_boundary >= distance:
                 around_map[location_name].append(location_nameB)
                 around_map[location_nameB].append(location_name)
      # 写入文件
      around_file = self.around_cf.get_str('storage','around_file')
      for location in around_map:
          around_line = location+':'+','.join(around_map[location])+'\n'
          self.write_to_file(around_file,around_line)

  def write_to_file(self, file_name, line, f_mode='a+'):
      f = open(file_name, f_mode)
      if isinstance(line, unicode):
         f.write(line.encode('utf8'))
      else:
         f.write(line)
      f.flush()
      f.close()

  def run(self):
      self.evaluate_location_around()

if __name__ == "__main__":
   ar = Around()
   ar.run()
