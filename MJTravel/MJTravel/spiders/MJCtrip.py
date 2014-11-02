# -*- coding: utf-8 -*-
import scrapy


class MjctripSpider(scrapy.Spider):
    name = "MJCtrip"
    allowed_domains = ["www.ctrip.com"]
    start_urls = (
        'http://www.ctrip.com/',
        'http://you.ctrip.com/travels/lushan20.html',
        'http://you.ctrip.com/travels/lushan20/1366778.html',
    )

    def parse(self, response):
        if '1366778.html' in response.url:
          from scrapy.shell import inspect_response
          inspect_response(response)
