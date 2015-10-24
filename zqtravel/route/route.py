# -*- coding: utf-8 -*-

# date: 07/23/2015
# author: Chen Chunyun
# program: Analyze routes

import os, re, sys, signal
from lib.mysql import Mysql
from lib.manufacture import ConfigMiaoJI
from lib.common_function import num_scenicspot_for_day
import requests
import urllib
import math, random
import traceback, logging
  
class RouteAnalyzer:
  def __init__(self):
      self.db_cf = ConfigMiaoJI("./conf/route.conf")
      self.my_db = self.connect_mysql()

  def update_lonlat_for_route(self):
    originid_sql = 'select id from Travelnotes_copy  where travels_score > "77"'
    lon_lat_sql1 = 'select Scenicspot_lon,Scenicspot_lat from Scenicspot where Scenicspot_name like "%s"'
    lon_lat_sql2 = 'select City_lon,City_lat from City where City_name like "%s"'
    route_sql = "select id,route,is_perfect from TravelRoute"
    originids = [x[0] for x in self.query_all_data(originid_sql)]
    routes = self.query_all_data(route_sql)
    for index, route in enumerate(routes):
      if index % 1000 == 0:
        print "Have dealed with: %d" % index if index != 0 else "Start update routes ..."
      did = route[0]
      scenicspots = route[1].replace(';',',').split(',')
      mid_num = len(scenicspots)/2 + len(scenicspots)%2 - 1
      mid_scenicspot = scenicspots[mid_num] if ":" not in scenicspots[mid_num] else scenicspots[mid_num].split(':')[1]
      lonlats = self.query_all_data(lon_lat_sql1 % mid_scenicspot)
      if not lonlats:
        lonlats = self.query_all_data(lon_lat_sql2 % mid_scenicspot)
      if lonlats and None not in lonlats[0]:
        lon, lat = lonlats[0]
      else:
        lon, lat = (0,0)
      is_perfect = "yes" if did in originids else "no"
      if route[2] is None:
        update_route_sql = 'update TravelRoute set lon=%f,lat=%f,is_perfect="%s" where id="%s"' % (lon, lat, is_perfect, did)
        self.update_from_db(update_route_sql, True)
    print "Done!"
    self.close_mysql()

  def update_route_fromDB(self):
    '''更新路线表（TravelRoute）'''
    route_sql = "select id,route from TravelRoute"      
    routes = self.query_all_data(route_sql)
    for index, route in enumerate(routes):
      if index % 1000 == 0:
        print "Have dealed with: %d" % index if index != 0 else "Start update routes ..."
      did = route[0]
      scenicspots = route[1].split('->')
      if 1 >= len(scenicspots):
        del_route_sql = 'delete from TravelRoute where id = "%s"' % (did)
        self.delete_from_db(del_route_sql, True)
      else:
        list_droute = []
        map_num_day = num_scenicspot_for_day(len(scenicspots))
        i=0
        while i < map_num_day["4scenicspots_day"]:
          j=i
          i += 1
          scenic_day = ','.join(scenicspots[4*j:4*i])
          list_droute.append(scenic_day)
        scenicspots_3 = scenicspots[map_num_day["4scenicspots_day"]*4:]
        i=0
        while i < map_num_day["3scenicspots_day"]:
          j=i
          i += 1
          scenic_day = ','.join(scenicspots_3[3*j:3*i])
          list_droute.append(scenic_day)
        scenicspots_2 = scenicspots[map_num_day["4scenicspots_day"]*4+map_num_day["3scenicspots_day"]*3:]
        i=0
        while i < map_num_day["2scenicspots_day"]:
          j=i
          i += 1
          scenic_day = ','.join(scenicspots_2[2*j:2*i])
          list_droute.append(scenic_day)
        random.shuffle(list_droute)
        title = u"%s%d天游" % (list_droute[0].split(',')[0], len(list_droute))
        days = u"%d天" % (len(list_droute))
        ddroute = ";".join([u"第"+str(i+1)+u"天:"+droute for i,droute in enumerate(list_droute)])
        update_route_sql = 'update TravelRoute set line_title="%s",route="%s",day_num="%s" where id="%s"' % (title, ddroute, days, did)
        self.update_from_db(update_route_sql, True)
    print "Done!"
    self.close_mysql()

  def analyze_origin_route(self):
      '''从Travelnotes_copy表中获取原始数据，处理得到路线信息'''
      route_location_file = self.db_cf.get_str('storage','route_location')
      route_sql = "select id,travels_title,travels_tips,scenicspot_locus from Travelnotes_copy"
      origin_routes = self.query_all_data(route_sql)
      tag_sql = "select Tag_name from Tag"
      tags = self.query_all_data(tag_sql)
      for index, o_route in enumerate(origin_routes):
          if index % 100 == 0:
             print "Have dealed with: %d" % index if index != 0 else "Starting analyzing routes ..."
          did = o_route[0]
          dline_title = o_route[1]
          dcity = o_route[3]
          droute = o_route[2].replace(',','->')
          dcrowd = 0
          dtag = set()
          scenic_pattern = re.compile(',')
          counts_of_scenicspot = len(scenic_pattern.findall(o_route[2]))
          if u'天' in droute:
             continue

          if 3 >= counts_of_scenicspot:
             dday_num = u"1天"
          if 5 >= counts_of_scenicspot > 3:
             dday_num = u"2天"
          if 8 >= counts_of_scenicspot > 5:
             dday_num = u"3天"
          if 11 >= counts_of_scenicspot > 8:
             dday_num = u"5天"
          if 12 <= counts_of_scenicspot:
             dday_num = u"7天+"

          for tag in tags:
              is_tag = set(droute) & set(tag[0])
              if is_tag:
                 dtag.add(tag[0])
          insert_sql = 'insert into TravelRoute(id,line_title,city,route,crowd,day_num,tag) values("%s","%s","%s","%s",%d,"%s","%s")' % (did,dline_title,dcity,droute,dcrowd,dday_num,','.join(dtag))
          try:
            self.instert_to_db(insert_sql)
          except:
            pass
      print "Done!"
      self.close_mysql()
  
  def run(self):
      #self.analyze_origin_route()
      #self.update_route_fromDB()
      self.update_lonlat_for_route()

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

  def instert_to_db(self, sql):
      self.my_db.insertone(sql)

  def query_all_data(self, sql):
      data = self.my_db.selectall(sql)
      return data

  def delete_from_db(self, sql, isAutoCommit=False):
      self.my_db.execute(sql, isAutoCommit)

  def update_from_db(self, sql, isAutoCommit=False):
      self.my_db.execute(sql, isAutoCommit)

  def close_mysql(self):
      self.my_db.close()
  
  def exit_prompt(self):
      print "Interrupted by user!"

if __name__ == "__main__":
   analyzer = RouteAnalyzer()
   analyzer.run()
