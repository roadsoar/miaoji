# -*- coding: utf-8 -*-
import scrapy


class MafengwoScenicspotSpider(scrapy.Spider):
    name = "mafengwo_scenicspot"
    allowed_domains = ["mafengwo.cn"]
    start_urls = (
        'http://www.mafengwo.cn/',
    )

    def parse(self, response):
        pass
