# -*- coding: utf-8 -*-

from zqtravel.items import MafengwoItem, ScenicspotItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log
import codecs
import scrapy

import re

#log.start(loglevel=log.DEBUG, logstdout=True)
mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MafengwoSpider(CrawlSpider):
    name = "mafengwo"
    allowed_domains = ["mafengwo.cn"]
    start_urls = mj_cf.get_starturls('mafengwo_spider','start_urls')

    #cities = '|'.join(mj_cf.get_allow_cities('ctrip_spider', 'allow_cities', 'disallow_cities'))
    #city_rules = ''.join(['/travels/(', cities, ')\d+.html'])
    #journey_rules = ''.join(['/travels/(', cities, ')\d+/\d+.html'])
    rules = [
             Rule(LxmlLinkExtractor('/mdd'),
             callback='parse_scenic_spots',
             follow=True),
             Rule(LxmlLinkExtractor('travel-scenic-spot/mafengwo/\d+.html'),
             callback='parse_next_pages',
             follow=True),
             Rule(LxmlLinkExtractor('baike/info-\d+.html'),
             callback='parse_next_pages',
             follow=True),
             Rule(LxmlLinkExtractor('yj/\d+/[\d-]+.html'),
             callback='parse_next_pages',
             follow=True),
            ]

    def parse_scenic_spots(self,response):
        """获得景点"""

        req = []
        scenicspot_item = ScenicspotItem()

        #re_travels_count = re.compile('>\s*\d+-(\d+)\s*/\s*(\d+)')
        province = remove_str(''.join(response.xpath('//div[@class="nav-item"][2]//dt/text()').extract()))
        scenicspot_item['province'] = province
        #log.msg(str(response.xpath('//div[@class="nav-item"][2]//h3/text()').extract()))
        scenicspot_hrefs = response.xpath('//div[@class="nav-item"][2]//@href').extract()

        url_prefix = self.get_url_prefix(response, True)

        # 景点url
        for href in scenicspot_hrefs:
            url = ''.join([url_prefix,href])
            r = Request(url, callback=self.parse_travel_next_pages, meta={'scenicspot_item':scenicspot_item})
            req.append(r)

        return req

    def parse_travel_next_pages(self,response):
        """获得游记下一页地址"""
        req = []

        travel_pages = response.xpath('//div[@class="wrapper"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
        travel_pages = int(''.join(travel_pages).strip())
        # 游记每一页url
        scenicspot_id = response.url[response.url.rfind('/')+1:-5]
        url_prefix = self.get_url_prefix(response, True)
        for page_index in range(1, travel_pages + 1):
            url = ''.join([url_prefix, '/yj/', scenicspot_id, '/2-0-', str(page_index), '.html'])
            yield  Request(url, callback=self.parse_travel_pages)
            #req.append(r)
        
        # 景点信息url
        url_info = ''.join([url_prefix, 'baike/info-', scenicspot_id, '.html'])
        yield Request(url_info, callback=self.parse_scenicspot_info, meta=response.meta)

        #return req
    def parse_scenicspot_info(self, response):
        pass

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
                   page_url_prefix = 'http://' + domain_name
                   break
        return page_url_prefix

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

        print req
        return req

    def parse_item(self, response):
       item = MafengwoItem()
       meta = response.meta

       # 游记链接
       link = response.url

       # 游记标题
       title = response.xpath("//div[@class='ctd_head_left']/h2/text()").extract()
       title = remove_str(title[0],'[\r\n\s]') if len(title) >= 1 else ''

       # 游记内容
       all_content = ""
       for content in response.xpath("//div[@class='ctd_main_body']//p/text()").extract():
         all_content += remove_str(remove_str(content,'\r'),'\s{2,}')

       # 游记浏览数
#       b_count = response.xpath("//a[@class='link_browse']/span/text()").extract()
       b_count = remove_str(meta['numview'][0]) if len(meta['numview']) >= 1 else '0'

       # 游记评论数
#       c_count = response.xpath("//a[@class='link_comment ']/span/text()").extract()
       c_count = remove_str(meta['numreply'][0]) if len(meta['numreply']) >= 1 else '0'

       item['travel_link'] = link
       item['travel_title'] = title
       item['travel_content'] = all_content
       item['browse_count'] = b_count
       item['comment_count'] = c_count

       # 丢弃游记内容是空的
       if item['travel_content'] == '':
         return None

       return item

