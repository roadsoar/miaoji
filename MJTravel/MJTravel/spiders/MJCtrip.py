# -*- coding: utf-8 -*-
import scrapy
from MJTravel.items import MjtravelItem
from MJTravel.manufacture import ConfigMiaoJI
import codecs

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MjctripSpider(scrapy.Spider):
    name = "MJCtrip"
    allowed_domains = ["www.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    def parse(self, response):
       for ctrip_p in response.xpath("//p/text()").extract():
         yield MjtravelItem(content=ctrip_p)
