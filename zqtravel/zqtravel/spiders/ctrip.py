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

        place_hrefs = response.xpath('//div[@class="footerseo"]/div[@class="footerseo_con"][1]/div[2]/a')
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        for href in place_hrefs:
            province_name = href.xpath('./text()').extract()
            province_name = ''.join(province_name).strip()
            province_url = href.xpath('./@href').extract()
            province_url = ''.join(province_url).strip()
            url = '%s%s' % (url_prefix, province_url)
            yield Request(url, callback=self.parse_city,meta={"province_name": province_name})

    def parse_city(self, response):
        '''抓取省下的城市的url, response.url => http://you.ctrip.com/countrysightlist'''

        url = response.url
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        province_name = response.meta.get('province_name', '')
        province_name = ''.join(province_name).strip()
        if province_name ==u"北京" or province_name ==u"上海" or province_name ==u"香港" or province_name ==u"澳门":
            city_href = re.sub(r'/place/', '/sight/', ''.join(url))
            yield Request(city_href, callback=self.parse_scenicspot_next_pages,meta={"city_name": province_name})
        city_href = re.sub(r'/place/', '/countrysightlist/', ''.join(url))
        #url = '%s%s' % (url_prefix, city_href)
        yield Request(city_href, callback=self.parse_city_pages)

    def parse_city_pages(self, response):
        #城市总页数
        city_pages = response.xpath('//div[@class="ttd_pager cf"]//b[@class="numpage"]/text()').extract()
        city_pages = int(''.join(city_pages).strip()) if len(city_pages) >= 1 else 1
        for page_index in range(1,city_pages+1):
            url = '%s%s%s%s' % ('.'.join(response.url.split('.')[:-1]),'/p',str(page_index),'.html')
            yield Request(url, callback=self.parse_city_scenicspot)

    def parse_city_scenicspot(self,response):
        #获取城市景点url
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        pre_xpath = '//div[@class="list_wide_mod1"]//%s'
        city_pages = response.xpath(pre_xpath % 'dt/a')
        for city in city_pages:
            city_name = city.xpath('./text()').extract()
            city_name = ''.join(city_name).strip()
            city_url = city.xpath('./@href').extract()
            city_href = re.sub(r'/place/', '/sight/', ''.join(city_url))
            url = '%s%s' % (url_prefix, city_href)
            yield Request(url, callback=self.parse_scenicspot_next_pages, meta={"city_name": city_name})

    def parse_scenicspot_next_pages(self, response):
        '''抓取城市景点页的url, response.url => http://you.ctrip.com/sight/lijiang32.html'''

        pre_xpath = '//div[@class="normalbox"]//div[@class="list_wide_mod2"]//%s'
        # 景点的总页数
        scenicspot_pages = response.xpath(pre_xpath % 'div[@class="pager_v1"]/span/b/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的景点
        scenicspot_pages = int(''.join(scenicspot_pages).strip()) if len(scenicspot_pages) >= 1 else 1

        sel_locus_infos = response.xpath('//div[@class="content cf "]//div[@class="breadbar_v1 cf"]/ul/li')
        province_name = sel_locus_infos[3].xpath('a/text()').extract()
        province_name = ''.join(province_name).strip(u'省')
        city_name = sel_locus_infos[-2].xpath('a/text()').extract()
        city_name = ''.join(city_name).strip(u'市')

        # 将城市的游记url写入文件
        data_dir = get_data_dir_with(province_name)
        file_name = '%s/%s' % (data_dir, province_name+'_travel.urls')
        youji_file = codecs.open(file_name, "a", encoding='utf-8')
        scenicspot_youji_url = re.sub(r'/sight/', '/travels/', response.url)
        youji_file.write('%s|%s|%s\n' % (province_name, city_name, scenicspot_youji_url))
        youji_file.flush()

        # 因为Scrapy的滤重，本页的景点也需要保证抓取到
        scenicspots = self.parse_scenicspot_pages(response, one_page=True, meta=response.meta)
        for scenicspot in scenicspots:
           yield scenicspot

        # 景点每一页url
        url_prefix = get_url_prefix(response, self.allowed_domains, False)
        page_href = response.xpath(pre_xpath % 'div[@class="pager_v1"]/a[@class="nextpage"]/@href').extract()
        page_href = ''.join(page_href).strip()
        for page_index in range(1,scenicspot_pages+1):
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

        pre_xpath = '//div[@class="normalbox boxsight_v1"]//div[@class="toggle_l"]//%s'
        # 景点介绍
        content = response.xpath(pre_xpath % 'p//text()').extract()
        content = ''.join(content).strip()
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
        traffic = response.xpath(pre_xpath1 % 'div[@class="text_style"]//p//text()').extract()
        traffic = ''.join(traffic).strip()

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
        #景区地址
        scenicspot_address = response.xpath('//div[@class="s_sight_infor"]//p[@class="s_sight_addr"]/text()').extract()
        scenicspot_address = ''.join(scenicspot_address).strip()
        #景点类型
        scenicspot_tag = response.xpath('//div[@class="s_sight_infor"]//ul[@class="s_sight_in_list"]/li[1]//a/text()').extract()
        scenicspot_tag = '|'.join(scenicspot_tag).strip()

        scenicspot_infos = response.xpath('//div[@class="s_sight_infor"]//ul[@class="s_sight_in_list"]//span[@class="s_sight_con"]/text()').extract()
        scenicspot_class = response.xpath('//div[@class="s_sight_infor"]//ul[@class="s_sight_in_list"]//span[@class="s_sight_classic"]/text()').extract()
        scenicspot_usedtime = ''
        scenicspot_webaddress = ''
        scenicspot_tel = ''
        for index, s_class in enumerate(scenicspot_class):
            if s_class.encode('utf-8').find('时间')>=0:
                scenicspot_usedtime = scenicspot_infos[index+1].strip()
            elif s_class.encode('utf-8').find('网站')>=0:
                scenicspot_webaddress = response.xpath('//div[@class="s_sight_infor"]//ul[@class="s_sight_in_list"]/li[last()]//a/text()').extract()
                scenicspot_webaddress = ''.join(scenicspot_webaddress).strip()
            elif s_class.encode('utf-8').find('话')>=0:
                scenicspot_tel = scenicspot_infos[index+1].strip()

        #开放时间
        scenicspot_opentime = response.xpath('//div[@class="s_sight_infor"]//dl[@class="s_sight_in_list"][1]/dd/text()').extract()
        scenicspot_opentime = ''.join(scenicspot_opentime).strip()
        #门票
        scenicspot_ticket = response.xpath('//div[@class="s_sight_infor"]//dl[@class="s_sight_in_list"][2]/dd/text()').extract()
        scenicspot_ticket = ''.join(scenicspot_ticket).strip()
        
        scenicspot_item['scenicspot_province'] = province_name
        scenicspot_item['scenicspot_locus'] = city_name 
        scenicspot_item['scenicspot_name'] = scenicspot_name
        scenicspot_item['scenicspot_grade'] = grade
        scenicspot_item['traffic'] = traffic
        scenicspot_item['scenicspot_commentnum'] = comment_num
        scenicspot_item['from_url'] = response.url
        scenicspot_item['scenicspot_address'] = scenicspot_address
        scenicspot_item['scenicspot_tag'] = scenicspot_tag
        scenicspot_item['scenicspot_usedtime'] = scenicspot_usedtime
        scenicspot_item['scenicspot_tel'] = scenicspot_tel
        scenicspot_item['scenicspot_webaddress'] = scenicspot_webaddress
        scenicspot_item['scenicspot_opentime'] = scenicspot_opentime
        scenicspot_item['scenicspot_ticket'] = scenicspot_ticket
        scenicspot_item['link'] = response.meta.get('link', '')
        scenicspot_item['scenicspot_intro'] = response.meta.get('content', '')
        
        # 将景点的游记url写入文件
        data_dir = get_data_dir_with(province_name)
        file_name = '%s/%s' % (data_dir, province_name+'_travel_city.urls')
        youji_file = codecs.open(file_name, "a", encoding='utf-8')
        scenicspot_youji_url = re.sub(r'-traffic\.html.*', '-travels.html', response.url)
        youji_file.write('%s|%s|%s|%s\n' % (province_name, city_name, scenicspot_name, scenicspot_youji_url))
        youji_file.flush()

        return scenicspot_item
