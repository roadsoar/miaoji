# -*- coding: utf-8 -*-
import scrapy


class ManSpider(scrapy.Spider):
    name = "man"
    allowed_domains = ["mafengwo.cn"]
    start_urls = (
        'http://www.mafengwo.cn/',
    )

    def parse(self, response):
        pass
