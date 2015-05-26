# -*- coding: utf-8 -*-

from zqtravel.items import CtripItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_url_prefix

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
             Rule(LxmlLinkExtractor(city_rules),
             callback='parse_next_pages',
             follow=True),
             Rule(LxmlLinkExtractor(journey_rules),
             callback='parse_next_pages',
             follow=True),
            ]

    def parse(self, response):
        '''抓取目的地的url, response.url => http://you.ctrip.com/'''

        place_href = response.xpath('//div[@class="gs-header cf"]//div[@class="gs-nav"]//li[@id="gs_nav_1"]/a/@href').extract()
        place_href = ''.join(place_href)
        url_prefix = get_url_prefix(response, True)
        url = '%s%s' % (url_prefix, place_href)
        yield Request(url, call_back=self.parse_city_scenicspots)

    def parse_city_scenicspots(self, response):
        '''抓取城市景点的url, response.url => http://you.ctrip.com/place'''

        sel_cities = response.xpath('//div[@class="desmap mod"]//div[@class="bd"]//dl[@class="item itempl-60"][2]//dd[@class="panel-con"]/ul//li')
        url_prefix = get_url_prefix(response, True)
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
                yield Request(url, call_back=self.parse_scenicspot_next_pages, meta={"city_name": city_name}

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
        url_prefix = get_url_prefix(response, True)
        page_href = response.xpath(pre_xpath % 'div[@class="pager_v1"]/a[@class="nextpage"]/@href').extract()
        page_href = ''.join(page_href)
        for page_index in range(scenicspot_pages, 1, -1):
            href = re.sub(r'-p\d+','-p'+str(page_index),page_href)
            url = '%s%s'(url_prefix, href)
            yield Request(url, callback=self.parse_scenicspot_pages, meta=response.meta)

    def parse_scenicspot_pages(self, response, one_page=False, meta={}):
        '''获得每页中景点的地址, response.url => http://you.ctrip.com/sight/jiuzhaigou25/s0-p5.html#sightname'''
        '''one_page: True=>用于表明抓取只有一个页面景点的城市'''
        '''meta:     当抓取只有一个页面景点的城市时，保存省名和城市名'''

        pre_xpath = '//div[@class="normalbox"]//div[@class="list_wide_mod2"]//%s'
        scenicspot_hrefs = response.xpath(pre_xpath % 'div[@class="list_mod2"]//div[@class="leftimg"]/a/@href').extract()

        url_prefix = get_url_prefix(response, True)
        for href in scenicspot_hrefs:
            url = '%s%s' % (url_prefix, href)
            yield Request(url, callback=self.parse_scenicspot_info_item, meta=response.meta)

    def parse_scenicspot_info_item(self, response):
        '''解析景点信息, response.url => http://you.ctrip.com/sight/jiuzhaigou25/1681356.html'''

        pre_xpath = '//div[@class="content cf dest_details"]//div[@class="normalbox boxsight_v1"]//%s'
        content = response.xpath(pre_xpath % 'li//text()' +'|' + 'p//text()' +'|'+ ).extract()
        content = ''.join(content)

    def parse_next_pages(self,response):
        """获得下一页地址"""
        req = []

        re_travels_count = re.compile('>\s*\d+-(\d+)\s*/\s*(\d+)')

        # 获取游记总页数
        travels_pages = 0
        travels_count_html = response.xpath('//div[@class="ttd2_background"]/div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]').extract()
        if travels_count_html:
          m = re_travels_count.search(travels_count_html[0])
          if m:
            records_per_page = int(m.group(1))
            travels_count = int(m.group(2))
            pages = travels_count / records_per_page
            travels_pages = pages if travels_count % records_per_page == 0 else pages + 1

        # 下一页地址
        page_url_prefix = self.get_url_prefix(response)

        for page_index in range(travels_pages, 0, -1):
            url = ''.join([page_url_prefix,'/s3-p',str(page_index), '.html'])
            r = Request(url, callback=self.parse_travel_pages)
            req.append(r)

        return req

    def parse_travel_pages(self, response):
        """获取游记页地址"""

        req = []
        
        href_list = response.xpath('//div[@class="ttd2_background"]/div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]//@href').extract()
        re_travel_href = re.compile('/[a-zA-Z]+/\w+/\d+\.html')

        page_url_prefix = self.get_url_prefix(response, splice_http=True)
        for href in href_list:
            m = re_travel_href.match(href)
            if m:
                numview = response.xpath('//div[@class="ttd2_background"]/div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]//a[@href="' + href +'"]//i[@class="numview"]/text()').extract()
                numreply = response.xpath('//div[@class="ttd2_background"]/div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]//a[@href="' + href +'"]//i[@class="numreply"]/text()').extract()
                url = ''.join([page_url_prefix, href])
                r = Request(url, callback=self.parse_item,meta={"numreply":numreply, "numview":numview})
                req.append(r)
               
        return req

    def parse_item(self, response):
       item = CtripItem()
       meta = response.meta
       
       # 游记链接
       link = response.url

       # 游记标题
       title = response.xpath("//div[@class='ctd_head_left']/h2/text()").extract()
       title = remove_str(''.join(title).strip(),'[\r\n\s]')

       # 游记内容
       all_content = ""
       for content in response.xpath("//div[@class='ctd_main_body']//p/text()").extract():
         all_content += remove_str(remove_str(content,'\r'),'\s{2,}')

       # 游记浏览数
#       b_count = response.xpath("//a[@class='link_browse']/span/text()").extract()
       b_count = remove_str(''.join(meta['numview']).strip())

       # 游记评论数
#       c_count = response.xpath("//a[@class='link_comment ']/span/text()").extract()
       c_count = remove_str(''.join(meta['numreply']).strip())

       # 游记评论
#       all_comment = []
#       for comment in response.xpath("//div[@class='ctd_comments_box cf']//p[@class='ctd_comments_text']/text()").extract():
#         all_comment.append(remove_str(remove_str(comment),'\s{2,}'))

       item['travel_link'] = link
       item['travel_title'] = title
       item['travel_content'] = all_content
       item['browse_count'] = b_count
       item['comment_count'] = c_count
#       item['comment_content'] = '|'.join(all_comment)

       # 丢弃游记内容是空的
       if item['travel_content'] == '':
         return None

       return item

