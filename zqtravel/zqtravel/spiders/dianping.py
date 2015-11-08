# -*- coding: utf-8 -*-

from zqtravel.items import POIItem
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

mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class DianpingSpider(scrapy.Spider):
    '''抓大众点评网的餐馆'''
    name = "dianping"
    allowed_domains = ["www.dianping.com"]
    start_urls = mj_cf.get_starturls('dianping_spider','start_urls')

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
               while step < len(href_and_city):
                   href = href_and_city[step]
                   if step == len(href_and_city)-1 or re.match('[a-z]+',href_and_city[step+1]):
                      city = href_and_city[step]
                      step +=1
                   else:
                      city = href_and_city[step+1]
                      step += 2
                   url = '%s%s' % (pre_url, href)
                   yield Request(url, callback=self.parse_city_meishi,meta={'province':province,'city':city})
            # 正常省份
            sel_provinces = sel_a.xpath('./dl[@class="terms"]')
            for sel_prov in sel_provinces:
              province = sel_prov.xpath('./dt/text()').extract()
              # href_and_city = ['shijiazhuang','石家庄','tangshan','唐山',...]
              href_and_city = sel_prov.xpath('.//dd//a/@href | .//dd//a/strong/text()').extract()
              step = 0
              # 轮询所属的所有城市
              while step < len(href_and_city):
                href = href_and_city[step]
                if step == len(href_and_city)-1 or re.match('[a-z]+',href_and_city[step+1]):
                   city = href_and_city[step]
                   step +=1
                else:
                   city = href_and_city[step+1]
                   step += 2
                url = '%s%s' % (pre_url, href)
                yield Request(url, callback=self.parse_city_meishi,meta={'province':province,'city':city})
    
    # response.url -> http://www.dianping.com/taiyuan
    def parse_city_meishi(self, response):
        pre_url = get_url_prefix(response, self.allowed_domains)
        meishi_xpath = '//div[@class="main page-home Fix"]//div[@class="section"]//div[@class="section-inner"]//div[@class="block popular-nav"]//ul[@class="term-list block-inner Fix"]//li[1]/ul/li//a[@class="more"]/@href'
        href = ''.join(response.xpath(meishi_xpath).extract())
        url = '%s%s' % (pre_url, href)
        yield Request(url, callback=self.parse_meishi, meta=response.meta)

    # response.url -> http://www.dianping.com/shopall/24/0
    def parse_meishi(self, response):
        pre_url = get_url_prefix(response, self.allowed_domains)
        sel_meishi_path = '//div[@class="main_w"]//div[@class="content_b"]//div[@class="box shopallCate"]//dl[1]//dd//ul//li'
        sel_meishi = response.xpath(sel_meishi_path)
        for href in sel_meishi.xpath('.//a/@href').extract():
            url = '%s%s' % (pre_url, ''.join(href))
            yield Request(url, callback=self.parse_canguan, meta=response.meta)

    # response.url -> http://www.dianping.com/search/category/24/10/g110p50
    def parse_canguan(self, response):
        pre_url = get_url_prefix(response, self.allowed_domains)

        # 获取第一页中的餐馆信息
        self.parse_canguan_info(response)

        page_num_path = '//div[@class="section Fix"]//div[@class="content-wrap"]//div[@class="shop-wrap"]//div[@class="page"]//a[last()-1]/text()'
        page_num = int(''.join(response.xpath(page_num_path).extract()))
        for pn in range(2,page_num+1):
           url = "%s%s%s" % (response.url,"p", str(pn)) 
           yield Request(url, callback=self.parse_canguan_info, meta=response.meta)

    # response.url -> http://www.dianping.com/search/category/24/10/g110p50p23
    def parse_canguan_info(self, response):
        poiitem = POIItem()
        meta = response.meta

        sel_xpath = '//div[@class="section Fix"]//div[@class="content-wrap"]//div[@class="shop-wrap"]//div[@class="content"]//div[@id="shop-all-list"]//ul//li'
        sel_poi = response.xpath(sel_xpath)
        pre_url = get_url_prefix(response, self.allowed_domains)
        for sel_p in sel_poi:
            pic = ''.join(sel_p.xpath('./div[@class="pic"]/a/img/@src').extract())
            href = ''.join(sel_p.xpath('./div[@class="pic"]/a/@href').extract())
            link = "%s%s" % (pre_url, href)
            name = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="tit"]/a/h4/text()').extract())
            star = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment"]/span/@title').extract())
            commentnum = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment"]//a[@class="review-num"]/b/text()').extract())
            cost1 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment"]//a[@class="mean-price"]/text()').extract())
            cost2 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment"]//a[@class="mean-price"]/b/text()').extract())
            cost = "%s %s" % (cost1, cost2)
            catalog = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="tag-addr"]//a[1]/span[@class="tag"]/text()').extract())
            addr1 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="tag-addr"]//a[2]/span[@class="tag"]/text()').extract())
            addr2 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="tag-addr"]//span[@class="addr"]/text()').extract())
            addr = "%s %s" % (addr1, addr2)
            kouwei1 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment-list"]/span[1]/text()').extract())
            kouwei2 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment-list"]/span[1]/b/text()').extract())
            kouwei = "%s %s" % (kouwei1, kouwei2)
            huanjing1 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment-list"]/span[2]/text()').extract())
            huanjing2 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment-list"]/span[2]/b/text()').extract())
            huanjing = "%s %s" % (huanjing1, huanjing2)
            service1 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment-list"]/span[3]/text()').extract())
            service2 = ''.join(sel_p.xpath('./div[@class="txt"]/div[@class="comment-list"]/span[3]/b/text()').extract())
            service = "%s %s" % (service1, service2)

            poiitem['poi_pic'] = pic
            poiitem['poi_link'] = link 
            poiitem['poi_name'] = name 
            poiitem['poi_star'] = star
            poiitem['poi_commentnum'] = commentnum 
            poiitem['poi_cost'] = cost
            poiitem['poi_catalog'] = catalog
            poiitem['poi_addr'] = addr
            poiitem['poi_kouwei'] = kouwei
            poiitem['poi_huanjing'] = huanjing
            poiitem['poi_service'] = service
            poiitem['from_url'] = response.url
            poiitem['province'] = meta.get('province') 
            poiitem['city'] = meta.get('city')

            return poiitem

