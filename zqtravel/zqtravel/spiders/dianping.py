# -*- coding: utf-8 -*-

from zqtravel.items import TravelItem, ScenicspotItem, ImageItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_data_dir_with, fetch_travel, get_url_prefix

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log 
import codecs

import scrapy
import re, os

class DianpingSpider(scrapy.Spider):
'''抓大众点评网的餐馆'''
    name = "dianping"
    allowed_domains = ["http://www.dianping.com/citylist"]
    start_urls = (
        'http://www.http://www.dianping.com/citylist/',
    )

    def parse(self, response):
        pass
