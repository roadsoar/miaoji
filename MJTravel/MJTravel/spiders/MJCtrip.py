# -*- coding: utf-8 -*-

from MJTravel.items import MjctripItem
from MJTravel.manufacture import ConfigMiaoJI
from MJTravel.lib.common import remove_str

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
import codecs
import scrapy

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MjctripSpider(CrawlSpider):
    name = "MJCtrip"
    allowed_domains = ["you.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor(allow='travels/haikou\d*/\d+'),
             callback='parse_item',
             follow=True),
             Rule(LxmlLinkExtractor(allow='travels/sanya\d*/\d+'),
             callback='parse_item',
             follow=True)
            ]

    def process_value(value):
      m = re.search("javascript:(.*?)", value)
      if m:
        return m.group(1)

    def parse_item(self, response):
       item = MjctripItem()
       
       # 游记链接
       link = response.url

       # 游记标题
       title = response.xpath("//div[@class='ctd_head_left']/h2/text()").extract()
       title = remove_str(title[0],'[\r\n\s]') if len(title) >= 1 else ''

       # 游记内容
       all_content = ""
       for content in response.xpath("//div[@class='ctd_main_body']//p/text()").extract():
         all_content += remove_str(remove_str(content,'\r'),'\s{2,}')

       # 游记浏览数
       b_count = response.xpath("//a[@class='link_browse']/span/text()").extract()
       b_count = remove_str(b_count[0]) if len(b_count) >= 1 else '0'

       # 游记评论数
       c_count = response.xpath("//a[@class='link_comment ']/span/text()").extract()
       c_count = remove_str(c_count[0]) if len(c_count) >= 1 else '0'

       # 游记评论
       all_comment = ""
       for comment in response.xpath("//div[@class='ctd_comments_box cf']//p[@class='ctd_comments_text']/text()").extract():
         all_comment += remove_str(remove_str(comment),'\s{2,}')

       item['travel_link'] = link
       item['travel_title'] = title
       item['travel_content'] = all_content
       item['browse_count'] = b_count
       item['comment_count'] = c_count
       item['comment_content'] = all_comment

       # 丢弃游记内容是空的
       if item['travel_content'] == '':
         return None

       return item

