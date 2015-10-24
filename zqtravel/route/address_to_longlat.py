# -*- coding: utf-8 -*-

# date: 07/03/2015
# author: Chen Chunyun
# program: Transform the address of scenic spot or city to longitude and latitude

import os, re, sys, signal
from lib.mysql import Mysql
from lib.manufacture import ConfigMiaoJI
import requests
import urllib
import math
import traceback, logging
  
class AddressAnalyzer:
  def __init__(self):
      self.db_cf = ConfigMiaoJI("./conf/route.conf")
      self.my_db = self.connect_mysql()

  def mercator2wgs84(self, mercator):
    point_x = mercator[0]
    point_y = mercator[1]
    x = point_x / 20037508.3319992 * 180
    y = point_y / 20037509.3427892 * 180
    y = 180/math.pi*(2*math.atan(math.exp(y*math.pi/180))-math.pi/2)
    return (x, y)
  
  def get_mercator(self, addr):
    pattern_x = re.compile(r'"x":(".+?")')
    pattern_y = re.compile(r'"y":(".+?")')
    if isinstance(addr, unicode):
       quote_addr = urllib.quote(addr.replace('.','').encode('utf-8'))
    else:
       quote_addr = urllib.quote(addr.replace('.',''))
    s = urllib.quote(u'北京市'.encode('utf8'))
    try:
      resolved_city_file = self.db_cf.get_str('storage','resolved_city_file')
      api_addr = "http://api.map.baidu.com/?qt=gc&wd=%s&cn=%s&ie=utf-8&oue=1&fromproduct=jsapi&res=api&callback=BMap._rd._cbk62300"%(quote_addr, s)
      req = requests.get(api_addr)
      content = req.content
      x = re.findall(pattern_x,content)
      y = re.findall(pattern_y,content)
      if x:
        x=x[0]
        y=y[0] 
        x=x[1:-1]
        y=y[1:-1]
        x=float(x)
        y=float(y)
        location = (x,y)
      else:
        location=()
      self.write_to_file(resolved_city_file, addr+'\n')
      return location
    except Exception as e:
      log_file = self.db_cf.get_str('logging','log')
      print "Occur broken errors, please logs (%s)." % (log_file) 
      traceback.print_exc(file=open(log_file,'a+'))
      sys.exit(-1)
  
  def get_location(self, addr):
    pattern_x = re.compile(r'"lng":(\d+.\d+)')
    pattern_y = re.compile(r'"lat":(\d+.\d+)')
    addr_list = addr.split('.')
    city_name = addr_list[1]
    province_name = addr_list[0]
    if len(addr_list) == 3:
       city_name = addr_list[2]
       province_name = addr_list[1]
    api_addr = 'http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=Pk0CeOPzsErMLmnbcY80uGWE&callback=showLocation' % addr.replace('.','')
    api_addr2 = 'http://api.map.baidu.com/geocoder/v2/?address=%s&city=%s&output=json&ak=Pk0CeOPzsErMLmnbcY80uGWE&callback=showLocation' % (city_name, province_name)
    api_addr3 = 'http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=Pk0CeOPzsErMLmnbcY80uGWE&callback=showLocation' % (city_name)

    try:
      resolved_city_file = self.db_cf.get_str('storage','resolved_city_file')
      req = requests.get(api_addr)
      content = req.content
      req2 = requests.get(api_addr2)
      content2 = req2.content
      req3 = requests.get(api_addr3)
      content3 = req3.content
      x = re.findall(pattern_x,''.join([content, content2, content3]))
      y = re.findall(pattern_y,''.join([content, content2, content3]))
      if x:
        x=x[0]
        y=y[0]
        location = (x,y)
      else:
        location=()
      self.write_to_file(resolved_city_file, addr+'\n')
      return location
    except Exception as e:
      log_file = self.db_cf.get_str('logging','log')
      print "Occur broken errors, please logs (%s)." % (log_file)
      traceback.print_exc(file=open(log_file,'w'))
      sys.exit(-1)

  def run(self):
    addrs = self.get_unresolved_city()  
    print "Dealing with longitude and latitude for City/Scenicspot.."
    addr_location_file = self.db_cf.get_str('storage','addr_location')
    for addr in addrs:
        mercator = self.get_location(addr)
        if not mercator:
           mercator = ('NotFound','NotFound')
        location = "%s,%s,%s\n"%(addr,mercator[0],mercator[1])
        self.write_to_file(addr_location_file, location)
    print "Done! Have %d City/Scenicspots." % len(addrs)

  def write_to_file(self, file_name, line, f_mode='a+'):
      f = open(file_name, f_mode)
      if isinstance(line, unicode):
         f.write(line.encode('utf8'))
      else:
         f.write(line)
      f.flush()
      f.close()
  
  def connect_mysql(self):
      host = self.db_cf.get_str('database', 'host')
      db_port = self.db_cf.get_int('database', 'port')
      db_user = self.db_cf.get_str('database', 'user')
      db_passwd = self.db_cf.get_str('database', 'passwd')
      db_name = self.db_cf.get_str('database', 'db')
      db = Mysql(host=host, port=db_port, user=db_user, passwd=db_passwd, database=db_name)
      db.connect()
      return db

  def query_cities(self):
      addr_list = []
      city_file = self.db_cf.get_str('storage','city_file')
      if os.path.isfile(city_file):
         print "Generating Scenicspot from local city file.."
         f = open(city_file)
         addr_list = [unicode(x.replace('\n',''),'utf-8') for x in f.readlines()]
         f.close()
      if not addr_list:
         print "Generating Scenicspot from database.."
         sql = "select Province.Province_name, City.City_name from Province, City where City.Province_no = Province.Province_no"
         #sql = "select Province.Province_name, City.City_name, Scenicspot_name from Province, City, Scenicspot where Scenicspot.City_no = City.City_no and City.Province_no = Province.Province_no"
         data = self.my_db.selectall(sql)
         self.close_mysql()
         for dt in data:
             addr = '.'.join(dt)
             addr_list.append(addr)       
         self.write_to_file(city_file, '\n'.join(addr_list))
      return addr_list

  def get_unresolved_city(self):
      addr_list = self.query_cities()
      resolved_list = []
      resolved_city_file = self.db_cf.get_str('storage','resolved_city_file')

      if os.path.isfile(resolved_city_file):
         f = open(resolved_city_file)
         resolved_list = [unicode(x.replace('\n',''),'utf-8') for x in f.readlines()]
         f.close() 
      return list(set(addr_list) - set(resolved_list)) 
  
  def close_mysql(self):
      self.my_db.close()
  
  def exit_prompt(self):
      print "Interrupted by user!"

if __name__ == "__main__":
   analyzer = AddressAnalyzer()
   analyzer.run()
