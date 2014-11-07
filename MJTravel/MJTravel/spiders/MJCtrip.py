# -*- coding: utf-8 -*-

from MJTravel.items import MjctripItem
from MJTravel.manufacture import ConfigMiaoJI
from MJTravel.lib.common import remove_str

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
import codecs
import scrapy

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MjctripSpider(CrawlSpider):
    name = "MJCtrip"
    allowed_domains = ["www.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    def parse(self, response):
       link = response.url
       title = response.xpath("//div[@class='ctd_head_left']/h2/text()").extract()
       if len(title) >= 1:  
         title = remove_str(title[0],'[\r\n\s]')
       else: 
         title = ''
       b_count = response.xpath("//a[@class='link_browse']/span/text()").extract()
       print "++++++++++++", b_count
       #if len(b_count >= 1)
       b_count = remove_str(b_count[0]) if len(b_count) >= 1 else '0'
       #else:
       #  b_count = '0'
       c_count = response.xpath("//a[@class='link_comment ']/span/text()").extract()
       if len(c_count) >= 1: 
         c_count = remove_str(c_count[0])
       else:
         c_count = '0'

       all_content = ""
       for content in response.xpath("//div[@class='ctd_main_body']//p/text()").extract():
         all_content += remove_str(remove_str(content,'\r'),'\s{2,}')

       all_comment = ""
       for comment in response.xpath("//p[@class='ctd_comments_text']/text()").extract():
         all_comment += remove_str(remove_str(comment),'\s{2,}')

       return MjctripItem(travel_link=link, travel_title=title, travel_content=all_content, browse_count=b_count, comment_count=c_count, comment_content=all_comment)

