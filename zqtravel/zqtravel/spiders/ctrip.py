# -*- coding: utf-8 -*-

from zqtravel.items import TravelItem, ScenicspotItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_url_prefix, get_data_dir_with

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log
import codecs
import scrapy

import re

log.start(loglevel=log.DEBUG, logstdout=True)
mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class CtripSpider(CrawlSpider):
    name = "ctrip"
    allowed_domains = ["you.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('ctrip.com'),
             callback='parse',
             follow=True),
            ]

    def parse(self, response):
        '''抓取目的地的url, response.url => http://you.ctrip.com/'''

        place_href = response.xpath('//div[@class="gs-header cf"]//div[@class="gs-nav"]//li[@id="gs_nav_1"]/a/@href').extract()
        place_href = ''.join(place_href)
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        url = '%s%s' % (url_prefix, place_href)
        yield Request(url, callback=self.parse_city_scenicspots)

    def parse_city_scenicspots(self, response):
        '''抓取城市景点的url, response.url => http://you.ctrip.com/place'''

        sel_cities = response.xpath('//div[@class="desmap mod"]//div[@class="bd"]//dl[@class="item itempl-60"][2]//dd[@class="panel-con"]/ul//li')
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        # 地区
        for sel_city in sel_cities:
            a_hrefs = sel_city.xpath('a')
            city_count = len(a_hrefs)
            # 地区下的城市
            for index in range(city_count-1, -1, -1):
                city_name = a_hrefs[index].xpath('./text()').extract()
                city_name = ''.join(city_name).strip
                city_href = a_hrefs[index].xpath('./@href').extract()
                city_href = re.sub(r'/place/', '/sight/', ''.join(city_href))
                url = '%s%s' % (url_prefix, city_href)
                yield Request(url, callback=self.parse_scenicspot_next_pages, meta={"city_name": city_name})

    def parse_scenicspot_next_pages(self, response):
        '''抓取城市景点页的url, response.url => http://you.ctrip.com/sight/lijiang32.html'''

        pre_xpath = '//div[@class="normalbox"]//div[@class="list_wide_mod2"]//%s'
        # 景点的总页数
        scenicspot_pages = response.xpath(pre_xpath % 'div[@class="pager_v1"]/span/b/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的景点
        scenicspot_pages = int(''.join(scenicspot_pages).strip()) if len(scenicspot_pages) >= 1 else 1
        # 因为Scrapy的滤重，本页的景点也需要保证抓取到
        scenicspots = self.parse_scenicspot_pages(response, one_page=True, meta=response.meta)
        for scenicspot in scenicspots:
           yield scenicspot

        # 景点每一页url
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        page_href = response.xpath(pre_xpath % 'div[@class="pager_v1"]/a[@class="nextpage"]/@href').extract()
        page_href = ''.join(page_href)
        for page_index in range(scenicspot_pages, 1, -1):
            href = re.sub(r'-p\d+','-p'+str(page_index),page_href)
            url = '%s%s' % (url_prefix, href)
            yield Request(url, callback=self.parse_scenicspot_pages, meta=response.meta)

    def parse_scenicspot_pages(self, response, one_page=False, meta={}):
        '''获得每页中景点的地址, response.url => http://you.ctrip.com/sight/jiuzhaigou25/s0-p5.html#sightname'''
        '''one_page: True=>用于表明抓取只有一个页面景点的城市'''
        '''meta:     当抓取只有一个页面景点的城市时，保存省名和城市名'''

        pre_xpath = '//div[@class="normalbox"]//div[@class="list_wide_mod2"]//%s'
        scenicspot_hrefs = response.xpath(pre_xpath % 'div[@class="list_mod2"]//div[@class="leftimg"]/a/@href').extract()

        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        for href in scenicspot_hrefs:
            url = '%s%s' % (url_prefix, href)
            yield Request(url, callback=self.parse_scenicspot_content, meta=response.meta)

    def parse_scenicspot_content(self, response):
        '''解析景点信息, response.url => http://you.ctrip.com/sight/jiuzhaigou25/1681356.html'''

        pre_xpath = '//div[@class="content cf dest_details"]//div[@class="normalbox boxsight_v1"]//%s'
        # 景点介绍
        content = response.xpath(pre_xpath % 'li//text()' +'|' + 'p//text()').extract()
        content = ''.join(content)
        meta_with_content = response.meta
        meta_with_content['content'] = content
        meta_with_content['link'] = response.url
        url = re.sub(r'.html', '-traffic.html', response.url)
        yield Request(url, callback=self.parse_scenicspot_jiaotong, meta=meta_with_content)

    def parse_scenicspot_jiaotong(self, response):
        '''解析景点信息, response.url => http://you.ctrip.com/sight/jiuzhaigou25/1681356-traffic.html#jiaotong '''
       
        scenicspot_item = ScenicspotItem()
        
        pre_xpath1 = '//div[@class="content cf dest_details"]//div[@class="normalbox current"]//%s'
        # 去景点的交通
        traffic = response.xpath(pre_xpath1 % 'div[@class="text_style"]//text()').extract()
        traffic = ''.join(traffic)

        pre_xpath2 = '//div[@class="content cf dest_details"]//div[@class="detailtop cf normalbox"]//ul[@class="detailtop_r_info"]//%s'
        # 景点的评分
        grade = response.xpath(pre_xpath2 % 'li[1]/span/b/text()').extract()
        grade = ''.join(grade)
        # 景点的评论数
        comment_num = response.xpath(pre_xpath2 % 'li[2]/span[@class="pl_num"]/a/span/text()').extract()
        comment_num = ''.join(comment_num)

        sel_locus_info = response.xpath('//div[@class="content cf "]//div[@class="breadbar_v1 cf"]/ul/li')
        # 省的名称
        province_name = sel_locus_info[3].xpath('a/text()').extract()
        province_name = ''.join(province_name).strip(u'省'+'\n\r '+u'景点')
        # 城市的名称
        city_name = sel_locus_info[-3].xpath('a/text()').extract()
        city_name = ''.join(city_name).strip(u'景点')
        # 景点的名称
        scenicspot_name = sel_locus_info[-2].xpath('a/text()').extract()
        scenicspot_name = ''.join(scenicspot_name).strip()

        scenicspot_item['scenicspot_province'] = province_name
        scenicspot_item['scenicspot_locus'] = city_name 
        scenicspot_item['scenicspot_name'] = scenicspot_name
        scenicspot_item['scenicspot_grade'] = grade
        scenicspot_item['traffic'] = traffic
        scenicspot_item['scenicspot_commentnum'] = comment_num
        scenicspot_item['from_url'] = response.url
        scenicspot_item['link'] = response.meta.get('link', '')
        scenicspot_item['scenicspot_intro'] = response.meta.get('content', '')
        
        # 将游记的url写入文件
        data_dir = get_data_dir_with(province_name)
        file_name = '%s/%s' % (data_dir, province_name+'_travel.urls')
        youji_file = codecs.open(file_name, "a", encoding='utf-8')
        scenicspot_youji_url = re.sub(r'-traffic\.html.*', '-travels.html', response.url)
        youji_file.write('%s|%s|%s|%s\n' % (province_name, city_name, scenicspot_name, scenicspot_youji_url))
        youji_file.flush()

        return scenicspot_item
