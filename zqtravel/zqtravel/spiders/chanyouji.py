# -*- coding: utf-8 -*-

from zqtravel.items import TravelItem, ScenicspotItem, ImageItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_data_dir_with

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log 
import codecs

import scrapy
import re, os


mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class ChanyoujiSpider(scrapy.Spider):
    '''爬取蝉游记的游记'''
    name = "chanyouji"
    allowed_domains = ["chanyouji.com"]
    start_urls = mj_cf.get_starturls('chanyouji_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('/poi/youji*'),
             callback='parse_travel_next_pages',
             follow=True),
             Rule(LxmlLinkExtractor('/i/\d+\.html'),
             callback='parse_scenicspot_travel_item',
             follow=True),
            ]

    def parse(self,response):
        pre_url = self.get_url_prefix(response, splice_http=True)
        youji_href = response.xpath('//div[@id="wrapper"]//div[@class="top-bar"]//ul[@class="menu"]//li[2]/a/@href').extract()
        youji_href = ''.join(youji_href).strip()

        # 国内游记url
        china_youji_url = '%s%s%s' % (pre_url, youji_href, '?type=china')
        yield Request(china_youji_url, callback=self.parse_province, meta=None)

    def parse_province(self, response):
        '''国内的response.url => http://chanyouji.com/trips?type=china'''

        pre_xpath = '//div[@id="wrapper"]//div[@id="page-body"]//div[@class="content-side"]//section[@class="open"]//ul[@class="clearfix"]//li//a//'
        province_hrefs = response.xpath(pre_xpath + '@href').extract()
        province_names = response.xpath(pre_xpath + 'text()').extract()

        url_prefix = self.get_url_prefix(response, True)

        for index, href in enumerate(province_hrefs):
            province_name = province_names[index]
            province_url = '%s%s' % (url_prefix, href)
            yield Request(province_url,callback=self.parse_travel_next_pages, meta={'province_name':province_name})

    def parse_travel_next_pages(self,response):
        """获得游记下一页地址, response.url => http://chanyouji.com/trips?destination_id=16&type=china"""
        '''last page href like href="/trips?destination_id=16&page=126&type=china'''

        pre_xpath = '//div[@id="wrapper"]//div[@id="page-body"]//div[@class="content-main"]//nav[@class="pagination"]//span[@class="last"]//'
        # 末页的href
        last_page_href = response.xpath(pre_xpath + '@href').extract()
        last_page_href = ''.join(last_page_href).strip()

        # 游记的总页数,如果没有获取到页数，则说明只有一页的游记
        travel_pages = int(re.sub(r'.*page=(\d+).*', '\g<1>', last_page_href)) if len(last_page_href)>=1 else 0

        # 为了抓取第一页面,直接调用获取游记页地址方法=>parse_travel_pages
        travel_urls = self.parse_travel_pages(response)
        for travel_url in travel_urls:
            yield travel_url

        url_prefix = self.get_url_prefix(response, True)
        for page_index in range(2, travel_pages + 1):
            page_href = re.sub('(.*page=)\d+(.*)', '\g<1>'+str(page_index)+'\g<2>', last_page_href)
            url = '%s%s' % (url_prefix, page_href)
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
        """获取游记页地址, reponse.url => http://chanyouji.com/trips?destination_id=25&page=3&type=china """

        pre_xpath = '//div[@id="wrapper"]//div[@id="page-body"]//div[@class="content-main"]//div[@class="all-trips clearfix"]//article[@class="trip-g"]//'
        # 所有游记链接
        href_list = response.xpath(pre_xpath + 'a[@class="cover"]/@href').extract()

        response.meta['from_url'] = response.url
        url_prefix = self.get_url_prefix(response, splice_http=True)
        for href in href_list:
            url = '%s%s' % (url_prefix, href)
            yield Request(url, callback=self.parse_travel_item, meta=response.meta)

    def parse_travel_item(self, response):
       '''获取游记内容, response.url => http://chanyouji.com/trips/149635 '''

       travel_item = TravelItem()

       pre_xpath ='//div[@id="js-trip"]//div[@class="trip-show-cover"]//div[@class="cover-header"]//'

       # 游记链接
       link = response.url

       # 游记标题 meta clearfix
       title = response.xpath(pre_xpath + 'h1[@id="js-cover-title"]//span[@class="inner-text"]/text()').extract()
       title = ''.join(title).strip()

       # 游记浏览数
       viewer_num = response.xpath(pre_xpath + 'div[@class="meta clearfix"]//div[@class="counter"]//span[@class="viewer-num"]/span/text()').extract()
       viewer_num = ''.join(viewer_num).strip()

       # 游记喜欢数
       liked_num = response.xpath(pre_xpath + 'div[@class="meta clearfix"]//div[@class="counter"]//span[@class="liked-num"]/span/text()').extract()
       liked_num = ''.join(liked_num).strip()

       # 游记评论数
       comments_num = response.xpath(pre_xpath + 'div[@class="meta clearfix"]//div[@class="counter"]//span[@class="comments-num"]/span/text()').extract()
       comments_num = ''.join(comments_num).strip()

       # 游记收藏数
       favorites_num = response.xpath(pre_xpath + 'div[@class="meta clearfix"]//div[@class="counter"]//span[@class="favorites-num"]/span/text()').extract()
       favorites_num = ''.join(favorites_num).strip()

       # 旅游的时间, 格式如："2014/10/6 [7天]"
       t_time = response.xpath(pre_xpath + 'div[@class="meta clearfix"]//div[@class="trip-info"]//time/text()').extract()
       t_time = ''.join(t_time).strip()
       # 游记时间和旅游的天数
       travel_days = ''
       travel_time = ''
       list_time = t_time.split()
       if len(list_time) > 1:
          travel_time = list_time[0]
          travel_days = re.sub(r'\[(.*)\]', '\g<1>', list_time[1])
       elif len(list_time) == 1:
          if list_time[0].find(u'天') == -1:
             travel_time = list_time[0]
          else:
             travel_days = list_time[0]

       pre_xpath_for_trip = '//div[@id="js-trip"]//article[@class="viewer"]//'

       # 旅游路线, 如：['第1天','大雁塔','兵马俑', ..., '第6天','游乐园','华山']
       medium_xpath_for_map = 'header[@id="trips-header"]//div[@class="trips-header"]//div[@class="trips-header"]//div[@class="trips clearfix"]//'
       xpath_for_map1 = '%s%s%s' % (pre_xpath_for_trip, 'div[@class="viewport-wrapper"]//div[@class="day-index"]/', 'text()')
       xpath_for_map2 = '%s%s%s' % (pre_xpath_for_trip, 'div[@class="note node"]', '//div[@class="node-name"]/text()')
       trip_roadmap = response.xpath(xpath_for_map1 +'|'+ xpath_for_map2).extract()
       trip = ''
       for i, roadmap in enumerate(trip_roadmap):
           if u'天' in roadmap:
              trip += ';'+roadmap if 0<i else roadmap
           else:
              trip += '|'+roadmap
       trip_roadmap = trip

       # 游记中涉及的景点
       sel_scenicspot_in_trip = response.xpath('//div[@class="node-info"]')
       scenicspot_in_trip = ''
       for i, sel_trip in enumerate(sel_scenicspot_in_trip):
           scenicspot_star = ''.join(sel_trip.xpath('.//i//@class').extract()).strip()
           scenicspot_ticket = ''.join(sel_trip.xpath('.//div[@class="memo"]//span//text()').extract()).strip()
           scenicspot_desc = ''.join(sel_trip.xpath('.//div[@class="desc"]//text()').extract()).strip()
           scenicspot = '|'.join([scenicspot_star, scenicspot_ticket, scenicspot_desc])
           scenicspot_in_trip += ';'+scenicspot if 0<i else scenicspot

       medium_xpath_for_content = 'div[@class="viewport-wrapper"]//div[@class="viewport"]//div[@class="slider"]//'
       # 游记内容
       xpath_for_content = '%s%s%s' % (pre_xpath_for_trip, medium_xpath_for_content,'p//text()')
       all_content = response.xpath(xpath_for_content).extract()
       all_content = remove_str(remove_str(''.join(all_content).strip()),'\s{2,}')

       roadmap_content = '|'.join([trip_roadmap, all_content])

       # 游记中的图片
       xpath_for_image = '%s%s' % ('//div[@class="extra-toolbar s-box"]','/div[@class="share-icons"]/div/@data-img')
       image_urls = response.xpath(xpath_for_image).extract()

       # 丢弃游记内容是空的
       if roadmap_content == '':
         return None

       # 设置游记中图片抓取的个数
       try:
          image_num = mj_cf.get_int('mafengwo_travel_spider','image_num_every_travel')
       except: # 如果没有设置，或设置错误则抓取游记中的全部图片
          image_num = None

       travel_item['travel_praisenum'] = favorites_num
       travel_item['travel_create_time'] = ''
       travel_item['travel_link'] = link
       travel_item['travel_title'] = title
       travel_item['trip_roadmap'] = trip_roadmap
       travel_item['travel_content'] = roadmap_content
       travel_item['travel_viewnum'] = viewer_num
       travel_item['travel_commentnum'] = comments_num
       travel_item['travel_time'] = travel_time
       travel_item['travel_people'] = ''
       travel_item['travel_cost'] = ''
       travel_item['travel_type'] = ''
       travel_item['travel_days'] = travel_days
       travel_item['scenicspot_province'] = response.meta.get('province_name')
       travel_item['from_url'] = response.meta.get('from_url')
       travel_item['image_urls'] = image_urls[:image_num]
       travel_item['scenicspot_in_trip'] = scenicspot_in_trip

       return travel_item

