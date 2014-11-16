# -*- coding: utf-8 -*-
import scrapy


class MafengwoSpider(scrapy.Spider):
    name = "mafengwo"
    allowed_domains = ["mafengwo.cn"]
    start_urls = (
        'http://www.mafengwo.cn/',
    )

    def parse(self, response):
        pass
