# -*- coding: utf-8 -*-

from zqtravel.items import CtripItem
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

log.start(loglevel=log.DEBUG, logstdout=True)
mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class CtripSpider(CrawlSpider):
    name = "ctrip"
    allowed_domains = ["you.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    cities = '|'.join(mj_cf.get_allow_cities('ctrip_spider', 'allow_cities', 'disallow_cities'))
    city_rules = ''.join(['/travels/(', cities, ')\d+.html'])
    journey_rules = ''.join(['/travels/(', cities, ')\d+/\d+.html'])
    rules = [
             Rule(LxmlLinkExtractor(city_rules),
             callback='parse_next_pages',
             follow=True),
             Rule(LxmlLinkExtractor(journey_rules),
             callback='parse_next_pages',
             follow=True),
            ]

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

        for page_index in range(1, travels_pages + 1):
            url = ''.join([page_url_prefix,'/s3-p',str(page_index), '.html'])
            r = Request(url, callback=self.parse_travel_pages)
            req.append(r)

        return req

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

