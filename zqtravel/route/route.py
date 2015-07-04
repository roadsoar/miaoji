# -*- coding: utf-8 -*-

import os, re
from lib.mysql import Mysql
from lib.manufacture import ConfigMiaoJI
import requests
import urllib
import math
  
  
class RouteAnalyzer:
  def __init__(self):
      self.db_cf = ConfigMiaoJI("./conf/route.conf")
      self.my_db = self.connect_mysql()

  def mercator2wgs84(self, mercator):
    point_x = mercator[0]
    point_y = mercator[1]
    x = point_x / 20037508.3427892 * 180
    y = point_y / 20037508.3427892 * 180
    y = 180/math.pi*(2*math.atan(math.exp(y*math.pi/180))-math.pi/2)
    return (x, y)
  
  def get_mercator(self, addr):
    pattern_x = re.compile(r'"x":(".+?")')
    pattern_y = re.compile(r'"y":(".+?")')
    quote_addr = urllib.quote(addr.encode('utf8'))
    s = urllib.quote(u'北京市'.encode('utf8'))
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
    return location
  
  def run(self):
    addrs = self.query_cities()  
    for addr in addrs:
        mercator = self.get_mercator(addr.replace('.',''))
        if mercator:
            wgs = self.mercator2wgs84(mercator)
        else:
            wgs=('NotFound','NotFound')
        location = "%s,%s,%s\n"%(addr,wgs[0],wgs[1])
        print location
        self.write_location_to_file(location)

  def write_location_to_file(self, line, f_mode='a+'):
      addr_location_file = self.db_cf.get_str('storage','addr_location')
      f = open(addr_location_file, f_mode)
      f.write(line.encode('utf8'))
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
      sql = "select Province.Province_name, City.City_name, Scenicspot_name from Province, City, Scenicspot where Scenicspot.City_no = City.City_no and City.Province_no = Province.Province_no limit 2;"
      data = self.my_db.selectall(sql)
      addr_list = []
      for dt in data:
        addr = '.'.join(dt)
        addr_list.append(addr)       
      return addr_list
  
  def close_mysql(self):
      self.my_db.close()

if __name__ == "__main__":
   ra = RouteAnalyzer()
   ra.run()
   ra.close_mysql()
