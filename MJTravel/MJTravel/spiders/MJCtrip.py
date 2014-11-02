# -*- coding: utf-8 -*-
import scrapy
from MJTravel.items import MjtravelItem
import codecs

class MjctripSpider(scrapy.Spider):
    name = "MJCtrip"
    allowed_domains = ["www.ctrip.com"]
    start_urls = (
       # 'http://www.ctrip.com/',
#        'http://you.ctrip.com/travels',
        'http://you.ctrip.com/travels/lushan20/1366778.html',
    )

    def parse(self, response):
          #from scrapy.shell import inspect_response
       for ctrip_p in response.xpath("//p/text()").extract():
         yield MjtravelItem(content=ctrip_p)
