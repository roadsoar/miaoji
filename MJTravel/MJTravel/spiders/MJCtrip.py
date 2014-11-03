# -*- coding: utf-8 -*-

import scrapy
from MJTravel.items import MjtravelItem
from MJTravel.manufacture import ConfigMiaoJI
from MJTravel.lib.common import remove_str
import codecs

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MjctripSpider(scrapy.Spider):
    name = "MJCtrip"
    allowed_domains = ["www.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    def parse(self, response):
       all_ctrip_p = ""
       for ctrip_p in response.xpath("//p/text()").extract():
         all_ctrip_p += remove_str(remove_str(ctrip_p), '\s{2,}|\|')
       return MjtravelItem(content=all_ctrip_p)

