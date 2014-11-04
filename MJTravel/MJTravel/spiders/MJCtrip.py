# -*- coding: utf-8 -*-

import scrapy
from MJTravel.items import MjctripItem
from MJTravel.manufacture import ConfigMiaoJI
from MJTravel.lib.common import remove_str
import codecs

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MjctripSpider(scrapy.Spider):
    name = "MJCtrip"
    allowed_domains = ["www.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    def parse(self, response):
       link = response.url
       title = response.xpath("//div[@class='ctd_head_left']/h2/text()").extract()
       if len(title) >= 1:  title = remove_str(title[0],'[\r\n\s]')
       b_count = response.xpath("//a[@class='link_browse']/span/text()").extract()
       print '++++++++++++++++++++++++++',b_count
       if len(b_count) >= 1: b_count = remove_str(b_count[0])
       c_count = response.xpath("//a[@class='link_comment ']/span/text()").extract()
       if len(c_count) >= 1: c_count = remove_str(c_count[0])

       all_ctrip_p = ""
       for ctrip_p in response.xpath("//div[@class='ctd_main_body']//p/text()").extract():
         all_ctrip_p += remove_str(remove_str(ctrip_p),'\s{2,}')

       all_comments = ""
       for comment in response.xpath("//div[@class='textarea_box fr']/p[@class='ctd_comments_text']/text()").extract():
         all_ctrip_p += remove_str(comment)

       return MjctripItem(travel_link=link, travel_title=title, travel_content=all_ctrip_p, browse_count=b_count, comment_count=c_count, comment_content=all_comments)

