# -*- coding: utf-8 -*-

from zqtravel.items import TravelItem, ScenicspotItem, ImageItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_data_dir_with, fetch_travel

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log 
import codecs

import scrapy
import re, os


mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class BreadtripSpider(scrapy.Spider):
    '''爬取面包旅行的游记'''
    name = "breadtrip"
    allowed_domains = ["breadtrip.com"]
    start_urls = mj_cf.get_starturls('breadtrip_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('/destinations/'),
             callback='parse',
             follow=True),
            ]

    def parse(self,response):
        """获得目的地的地址, response.url => http://breadtrip.com/ """

        url_prefix = self.get_url_prefix(response, splice_http=True)
        dest_url = response.xpath('//div[@class="top-nav"]//div[@class="nav-bar float-left"]//a[@class="destination "]/@href').extract()
        dest_url = ''.join(dest_url).strip()
        url = '%s%s' % (url_prefix, dest_url)

        yield Request(url, callback=self.parse_city)

    def parse_city(self, response):
        """获得城市的地址, response.url => http://breadtrip.com/destinations/ """

        all_xpath = '//div[@id="domestic-dest-popup"]//div[@class="content"]//ul//li'
        all_cities = response.xpath(all_xpath)

        url_prefix = self.get_url_prefix(response, splice_http=True)
        for sel_city in all_cities:
            province_name = sel_city.xpath('div[@class="level-1 clear-both"]/text()').extract()
            province_name = ''.join(province_name).strip()
            city_list = sel_city.xpath('div[@class="level-2 float-left"]//a/span[@class="ellipsis_text"]/text()').extract()
            href_list = sel_city.xpath('div[@class="level-2 float-left"]//a/@href').extract()
            for city_name, href in zip(city_list, href_list):
                city_name = city_name.strip()
                url = '%s%s' % (url_prefix, href)
                yield Request(url, callback=self.parse_travel_next_pages, meta={"province_name": province_name, "city_name":city_name})

    def parse_travel_next_pages(self, response):
        """获得游记页的地址, response.url => http://breadtrip.com/scenic/3/1/trip/#nav """

        scenicspot_href = response.xpath('//div[@class="wrap"]//ul[@class="nav  nav-city"]//li[3]/a/@href').extract()
        scenicspot_href = ''.join(scenicspot_href).strip().split('#')[0]
        url_prefix = self.get_url_prefix(response, splice_http=True)       
        url = '%s%s%s%s' % (url_prefix, scenicspot_href, 'more/?next_start=', "0")
        yield Request(url, callback=self.parse_travel_pages, meta=response.meta)


    def get_url_prefix(self, response, splice_http=False):
        page_url_prefix = ''

        if not splice_http:
            for domain_name in self.allowed_domains:
                if domain_name in response.url:
                   page_url_prefix = response.url[0:-5]
                   break
        else:
            for domain_name in self.allowed_domains:
                if domain_name in response.url:
                   page_url_prefix = 'http://www.' + domain_name
                   break
        return page_url_prefix

    def parse_travel_pages(self, response):
        """获得游记的地址, response.url => http://breadtrip.com/scenic/3/333/trip/more/?next_start=0 """
        
        meta_with_from_url = response.meta
        meta_with_from_url['from_url'] = response.url
        travel_url = re.findall(r'(/scenic/\d+/\d+/trip/more/\?next_start=\d+)', response.body)
        travel_url = ''.join(travel_url).strip()
        travel_hrefs = re.findall(r'"encrypt_id": (\d+)', response.body)
        url_prefix = self.get_url_prefix(response, splice_http=True)
        if  travel_url!='':
            url = '%s%s' % (url_prefix,travel_url)
            scrapy.log.msg(url)
            yield Request(url, callback=self.parse_travel_pages, meta=response.meta)
        for href in travel_hrefs:
            url = '%s%s%s%s' % (url_prefix, '/trips/', href,'/schedule_line/')
            yield Request(url, callback=self.parse_travel_schedule_line, meta=meta_with_from_url)
            


    def parse_travel_schedule_line(self,response):
        meta_with_line = response.meta
        xpath_for_map1 = '%s%s' % ('//dt[@class="day-marker"]//span[2]/', 'text()')
        xpath_for_map2 = '%s%s' % ('//div[@class="city-info"]', '//p[@class="city-name fl"]//span/text()')
        xpath_for_map3 = '%s%s' % ('//ul[@class="poi"]', '//a/text()')
        trip_roadmap = response.xpath(xpath_for_map1 +'|'+ xpath_for_map2+'|'+ xpath_for_map3).extract()
        scenicspot = response.xpath(xpath_for_map3).extract()
        trip = ''
        for i, roadmap in enumerate(trip_roadmap):
            if re.match(u'第\d+天', roadmap):
                trip += '|'+roadmap+':' if 0<i else roadmap+':'
            else:
                trip += roadmap+',' if i<len(trip_roadmap)-1 else roadmap
        trip_roadmap = re.sub(r',\|', '|', trip)
        meta_with_line['trip_roadmap'] = trip_roadmap
        meta_with_line['scenicspot_in_trip']= scenicspot
        url = response.url
        item = url.split("/")
        url = "/".join(item[:-2])
        yield Request(url, callback=self.parse_scenicspot_travel_item, meta=meta_with_line)
        

    def parse_scenicspot_travel_item(self, response):

       travel_item = TravelItem()
       meta = response.meta

       # 游记链接
       link = response.url

       pre_trip_info_xpath = '//div[@id="content"]//div[@id="trip-info"]//div[@class="trip-summary fl"]//%s'
       # 游记标题
       title = response.xpath(pre_trip_info_xpath % 'h2/text()').extract()
       title = ''.join(title).strip()
       title = re.sub(u'[“”‘’"\']', '', title)

       # 旅游的天数 
       travel_days = response.xpath(pre_trip_info_xpath % 'p/span[2]/text()').extract()
       travel_days = ''.join(travel_days).strip()
       if int(travel_days[:-1]) > 200:
          return None

       # 旅游的开始时间
       travel_time = response.xpath(pre_trip_info_xpath % 'p/span[1]/text()').extract()
       travel_time = ''.join(travel_time).strip()

       # 游记浏览数
       numview = response.xpath(pre_trip_info_xpath % 'p/span[@class="trip-pv"]/b/text()').extract()
       numview = ''.join(numview).strip()

       pre_trip_info_xpath2 = '//div[@id="content"]//div[@id="trip-info"]//div[@class="trip-tools ibfix fr"]//%s'
       # 游记评论数
       commentnum = response.xpath(pre_trip_info_xpath2 % 'a[@class="ibfix-c trip-tools-comment"]/b/text()').extract()
       commentnum = ''.join(commentnum).strip()

       # 游记被赞或顶的数量
       travel_praisenum = response.xpath(pre_trip_info_xpath2 % 'a[@class="ibfix-c first trip-tools-bookmark"]/b/text()').extract()
       travel_praisenum = ''.join(travel_praisenum).strip()


       # 游记创建时间
       travel_create_time = ''

       # 游记内容
       # 蚂蜂窝的游记页面使用了多种模板，所以对照的写了些xpath
       pre_content_xpath = '//div[@id="content"]//div[@class="trip-wps"]//%s'
       all_content = response.xpath(pre_content_xpath % 'p//text()' +'|'+ pre_content_xpath % 'a//@data-caption' +'|'+ pre_content_xpath % 'h3//text()' +'|'+ pre_content_xpath % 'div//p/text()').extract()
       all_content = remove_str(remove_str(''.join(all_content).strip()),'\s{2,}')
       all_content = re.sub(u'[“”‘’"\']', '', all_content)

       # 游记中的图片
       image_urls = response.xpath(pre_content_xpath % 'div[@class="photo-ctn"]//a/@href').extract()

       # 如果设置并开启了爬取的开始时间，则将早于开始时间的游记丢弃
       enable_start_crawling_time = mj_cf.get_str('mafengwo_spider','enable_start_crawling_time')
       if enable_start_crawling_time == 'True':
          start_crawling_time = mj_cf.get_str('mafengwo_spider','start_crawling_time')
          if travel_time < start_crawling_time:
             return None

       # 丢弃游记内容是空的
       if all_content == '':
         return None
        
       # 丢弃不包含图片的游记
       if not image_urls:
         return None
      
       # 丢弃3年以前或不符合抓取规则的游记
       if not fetch_travel(travel_time, numview):
          return None

       try:
          image_num = mj_cf.get_int('breadtrip_spider','image_num_every_travel')
       except: # 如果没有设置，或设置错误则抓取游记中的全部图片
          image_num = None

       travel_item['travel_praisenum'] = travel_praisenum
       travel_item['travel_create_time'] = travel_create_time
       travel_item['travel_link'] = link
       travel_item['travel_title'] = title
       travel_item['travel_content'] = all_content
       travel_item['travel_viewnum'] = numview
       travel_item['travel_commentnum'] = commentnum
       travel_item['travel_time'] = travel_time
#       travel_item['travel_people'] = travel_people
#       travel_item['travel_cost'] = travel_cost
#       travel_item['travel_type'] = travel_type
       travel_item['travel_days'] = travel_days
       travel_item['scenicspot_in_trip'] = meta.get('scenicspot_in_trip')
       travel_item['trip_roadmap'] = meta.get('trip_roadmap')
       travel_item['scenicspot_province'] = meta.get('province_name')
       travel_item['scenicspot_locus'] = meta.get('city_name')
       #travel_item['scenicspot_name'] = meta.get('scenicspot_name')
       travel_item['from_url'] = meta.get('from_url')
       travel_item['image_urls'] = image_urls[:image_num]

       return travel_item

