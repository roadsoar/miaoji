# -*- coding: utf-8 -*-

from zqtravel.items import TravelItem, ScenicspotItem, ImageItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_data_dir_with, fetch_travel, get_url_prefix

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log 
import codecs

import scrapy
import re, os

class DianpingSpider(scrapy.Spider):
'''抓大众点评网的餐馆'''
    name = "dianping"
    allowed_domains = ["www.dianping.com"]
    start_urls = (
        'http://www.dianping.com/citylist',
    )

    def parse(self, response):
        url = "%s/%s" % (response.url, "citylist?citypage=1")
        yield Request(url, callback=self.parse_cities)

    def parse_cities(self, response):
        sel_xpath = '//div[@class="main page-cityList"]//div[@class="section"]//ul[@class="glossary-list gl-region"]//li'
        sel_as = response.xpath(sel_xpath)
        pre_url = get_url_prefix(response, self.allowed_domains)
        for index, sel_a in enumerate(sel_as):
            # 直辖市或港澳台
            if index <= 1:
               province = sel_a.xpath('./strong[@class="vocabulary"]/text()').extract()
               # href_and_city = ['shanghai','上海','beijing','北京',...]
               href_and_city = sel_a.xpath('./div[@class="terms"]//a/@href | ./div[@class="terms"]//a/strong/text()').extract()
               step = 0
               # 轮询所属的所有城市
               while step <= len(href_and_city):
                   href = href_and_city[step]
                   city = href_and_city[step+1]
                   step += 2
                   url = '%s%s' % (pre_url, href)
                   yield Request(url, callback=self.parse_city_meishi,meta={'province':province,'city':city})
            # 正常省份
            sel_provinces = sel_a.xpath('./dl[@class="terms"])')
            for sel_prov in sel_provinces:
              province = sel_prov.xpath('./dt/text()').extract()
              # href_and_city = ['shijiazhuang','石家庄','tangshan','唐山',...]
              href_and_city = sel_prov.xpath('.//dd//a/@href | .//dd//a/strong/text()').extract()
              step = 0
              # 轮询所属的所有城市
              while step <= len(href_and_city):
                href = href_and_city[step]
                city = href_and_city[step+1]
                step += 2
                url = '%s%s' % (pre_url, href)
                yield Request(url, callback=self.parse_city_meishi,meta={'province':province,'city':city})
    
    # response.url -> http://www.dianping.com/taiyuan
    def parse_city_meishi(self, response):
        pre_url = get_url_prefix(response, self.allowed_domains)
        meishi_xpath = '//div[@class="main page-home Fix"]//div[@class="section"]//div[@class="section-inner"]//div[@class="block popular-nav"]//ul[@class="term-list block-inner Fix"]//li[1]/ul/li//a[@class="more"]/@href'
        href = response.xpath(meishi_xpath).extract()
        url = '%s%s' % (pre_url, href)
        yield Request(url, callback=self.parse_meishi, meta=response.meta)

    # response.url -> http://www.dianping.com/shopall/24/0
    def parse_meishi(self, response):
        pre_url = get_url_prefix(response, self.allowed_domains)
        sel_meishi_path = '//div[@class="main_w"]//div[@class="content_b"]//div[@class="box shopallCate"]//dl[1]//dd//ul//li'
        sel_meishi = reponse.xpath(sel_meishi_path)
        for href in sel_meishi.xpath('.//a/@href').extract():
            url = '%s%s' % (pre_url, href)
            yield Request(url, callback=self.parse_canguan, meta=response.meta)

    # response.url -> http://www.dianping.com/search/category/24/10/g110p50
    def parse_canguan(self, response):
        pre_url = get_url_prefix(response, self.allowed_domains)

        # 获取第一页中的餐馆信息
        slef.parse_canguan_info(response)

        page_num_path = '//div[@class="section Fix"]//div[@class="content-wrap"]//div[@class="shop-wrap"]//div[@class="page"]//a[latest()-1]'
        page_num = int(response.xpath(page_num_path).extract())
        for pn in range(2,page_num+1):
           url = "%s%s%s" % (response.url,"p", str(pn)) 
           yield Request(url, callback=self.parse_canguan_info, meta=response.meta)

    # response.url -> http://www.dianping.com/search/category/24/10/g110p50p23
    def parse_canguan_info(self, response):
        meta = response.meta
