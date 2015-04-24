# -*- coding: utf-8 -*-

from zqtravel.items import MafengwoItem, ScenicspotItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_data_dir_with

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log 
import codecs

import scrapy
import re, os


mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class MafengwoTravelSpider(scrapy.Spider):
    '''爬取蚂蜂窝的游记'''
    name = "mafengwo_travel"
    allowed_domains = ["mafengwo.cn"]
    start_urls = mj_cf.get_starturls('mafengwo_travel_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('/poi/youji*'),
             callback='parse_travel_pages',
             follow=True),
             Rule(LxmlLinkExtractor('/i/\d+\.html'),
             callback='parse_scenicspot_travel_item',
             follow=True),
            ]

    def parse(self,response):
        travel_urls_root_dir = mj_cf.get_str('mafengwo_travel_spider','travel_urls_dir')
        travel_provinces = mj_cf.get_list('mafengwo_travel_spider','travel_provinces')
        # 爬取所有省份
        if 'all' in travel_provinces:
           for dirpath, subdir_names, filenames in os.walk(travel_urls_root_dir):
               if filenames:
                  travel_urls_file = os.path.join(dirpath,filenames[0])
                  travel_urls = self.trigger_travel_url_from(travel_urls_file)
                  for travel_url in travel_urls:
                      yield travel_url
        # 爬取部分省份
        else:
            for province in travel_provinces:
                travel_urls_file = os.path.join(travel_urls_root_dir, province, province+'_travel.urls')
                travel_urls = self.trigger_travel_url_from(travel_urls_file)
                for travel_url in travel_urls:
                    yield travel_url

    def trigger_travel_url_from(self, travel_urls_file):
        f_all_urls = open(travel_urls_file, 'r')
        for line in f_all_urls.readlines():
            line_list = line.split('|')
            scenicspot_province = line_list[0]
            scenicspot_locus = line_list[1]
            scenicspot_name = line_list[2]
            scenicspot_info = {}
            scenicspot_info['scenicspot_province'] = scenicspot_province
            scenicspot_info['scenicspot_locus'] = scenicspot_locus
            scenicspot_info['scenicspot_name'] = scenicspot_name 
            travel_url = line_list[-1].strip()
            yield Request(travel_url, callback=self.parse_travel_next_pages, meta={'scenicspot_info':scenicspot_info})
        f_all_urls.close()

    def parse_travel_next_pages(self,response):
        """获得游记下一页地址"""

        # 游记的总页数
        travel_pages = response.xpath('//div[@class="wrapper"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的游记
        travel_pages = int(''.join(travel_pages).strip()) if len(travel_pages)>=1 else 0

        # 只有一页游记
        if not travel_pages:
           # 直接调用获取游记页地址方法=>parse_travel_pages
           travel_urls = self.parse_travel_pages(response)
           for travel_url in travel_urls:
               yield travel_url
        # 多页
#        else:
#          fetch_js = mj_cf.get_starturls('mafengwo_travel_spider','fetch_js')
#          # 抓取的动态网页
#          if fetch_js:
#             travel_id = response.url[response.url.rfind('/')+1:-5]
#             url_prefix = self.get_url_prefix(response, True)
#             for page_index in range(1, travel_pages + 1):
#                 url = ''.join([url_prefix, '/yj/', travel_id, '/1-0-', str(page_index), '.html'])
#                 yield Request(url, callback=self.parse_travel_pages, meta=response.meta)
#          # 非动态网页
#          else:
#             travel_id = response.url[response.url.rfind('/')+1:-5]
#             url_prefix = self.get_url_prefix(response, True)
#             for page_index in range(1, travel_pages + 1):
#                 url = ''.join([url_prefix, '/yj/', travel_id, '/1-0-', str(page_index), '.html'])
#                 yield Request(url, callback=self.parse_travel_pages, meta=response.meta)

    def get_url_prefix(self, response, splice_http=False):
        page_url_prefix = ''

        if not splice_http:
            for domain_name in self.allowed_domains:
                if domain_name in response.url:
                   page_url_prefix = response.url[0:-5]
                   break
        else:
            for domain_name in self.allowed_domains:
                if domain_name in response.url:
                   page_url_prefix = 'http://www.' + domain_name
                   break
        return page_url_prefix

    def parse_travel_pages(self, response):
        """获取游记页地址"""

        tmp_item = response.meta.get('scenicspot_info')
        scenicspot_province = tmp_item.get('scenicspot_province')
        scenicspot_locus = tmp_item.get('scenicspot_locus')
        scenicspot_name = tmp_item.get('scenicspot_name')

        # 所有游记链接
        youji_pre_xpath ='//div[@class="wrapper"]//div[@class="p-content"]//div[@class="m-post"]//ul//li[@class="post-item clearfix"]//'
        href_list = response.xpath(youji_pre_xpath + 'h2[@class="post-title yahei"]/a/@href').extract()

        re_travel_href = re.compile('/i/\d+\.html')

        numview_numreply = response.xpath(youji_pre_xpath + 'span[@class="status"]/text()').extract()
        ## numview_numreply output format:
        ##  numview numreply, numview numreply ...
        ## [u'2824', u'13',  u'2462', u'27',   u'9594', u'24', u'2326', u'22', u'2345', u'7'] 
        ## 浏览数和评论数的对数跟页面中游记连接条数是一致的, 如：http://www.mafengwo.cn/poi/youji-21100.html
        url_prefix = self.get_url_prefix(response, splice_http=True)
        num_index = 0
        for href in href_list:
            m = re_travel_href.match(href)
            if m:
                numview = numview_numreply[num_index]
                numreply = numview_numreply[num_index+1]
                num_index += 2 # 以及上面numview_numreply的输出格式，每次的步数为2
                url = ''.join([url_prefix, href])
                meta_data = {"numreply":numreply, \
                             "numview":numview, \
                             "scenicspot_province":scenicspot_province, \
                             "scenicspot_locus":scenicspot_locus, \
                             "scenicspot_name":scenicspot_name, \
                             "from_url":response.url \
                            }
                yield Request(url, callback=self.parse_scenicspot_travel_item,meta=meta_data)

    def parse_scenicspot_travel_item(self, response):

       travel_item = MafengwoItem()
       meta = response.meta

       # 游记链接
       link = response.url

       # 游记标题
       title = response.xpath('//div[@class="post-hd"]//div[@class="post_title clearfix"]/h1/text() |\
                              //div[@class="view_info"]//div[@class="vi_con"]/h1/text()' \
                             ).extract()
       title = remove_str(title[0],'[\r\n\s]') if len(title) >= 1 else ''

       # 游记创建时间
       travel_create_time = response.xpath('//div[@class="post_item"]//div[@class="tools no-bg"]//div[@class="fl"]//span[@class="date"]/text() |\
                                      //div[@class="view clearfix"]//div[@class="vc_title clearfix"]//div[@class="vc_time"]/span[@class="time"]/text()' \
                                    ).extract()
       travel_create_time = ''.join(travel_create_time).strip()

       xpath_with_blank_pre = '//div[@class="post_wrap"]//div[@class="post_main "]//div[@class="post_info"]//div[@id="exinfo-tripinfo"]//div[@class="basic-info"]//li[@class="%s"]//text()'
       xpath_without_blank_pre = '//div[@class="post_wrap"]//div[@class="post_main"]//div[@class="post_info"]//div[@id="exinfo-tripinfo"]//div[@class="basic-info"]//li[@class="%s"]//text()'
       # 得到类似数据:[u'天数', u'7', u'天'],所以用[1:]截取后面的实际数值
       travel_time = response.xpath(xpath_with_blank_pre % 'item-date'+'|'+xpath_without_blank_pre % 'item-date').extract()
       travel_time = ''.join(travel_time[1:]).strip()

       travel_people = response.xpath(xpath_with_blank_pre % 'item-people'+'|'+xpath_without_blank_pre % 'item-people').extract()
       travel_people = ''.join(travel_people[1:]).strip()

       travel_cost = response.xpath(xpath_with_blank_pre % 'item-cost'+'|'+xpath_without_blank_pre % 'item-cost').extract()
       travel_cost = ''.join(travel_cost[1:]).strip()

       travel_type= response.xpath(xpath_with_blank_pre % 'item-type'+'|'+xpath_without_blank_pre % 'item-type').extract()
       travel_type = ''.join(travel_type[1:]).strip()

       travel_days = response.xpath(xpath_with_blank_pre % 'item-days'+'|'+xpath_without_blank_pre % 'item-days').extract()
       travel_days = ''.join(travel_days[1:]).strip()

       # 游记内容
       # 蚂蜂窝的游记页面使用了多种模板，所以对照的写了些xpath
       all_content = response.xpath('//div[@class="post_item"]//div[@id="pnl_contentinfo"]//p/text() |\
                                     //div[@class="post_item"]//div[@id="pnl_contentinfo"]/text() |\
                                     //div[@class="post_item"]//div[@id="pnl_contentinfo"]//br/text() |\
                                     //div[@class="view clearfix"]//div[@class="vc_article"]//div[@class="va_con"]//p//text() |\
                                     //div[@class="view clearfix"]//div[@class="vc_article"]//div[@class="va_con"]//a//text()' \
                                   ).extract()
       all_content = remove_str(remove_str(''.join(all_content).strip()),'\s{2,}')

       # 游记浏览数
       b_count = ''.join(meta['numview']).strip()

       # 游记评论数
       c_count = ''.join(meta['numreply']).strip()

       # 游记被赞或顶的数量
       travel_praisenum = response.xpath('//div[@class="post-hd"]//div[@class="bar_share"]/div[@class="post-up"]/div[@class="num _j_up_num"]/text() |\
                                           //div[@class="view clearfix"]//div[@class="ding"]/strong/text()' \
                                         ).extract()
       travel_praisenum = ''.join(travel_praisenum).strip()

       # 游记中的图片
       image_urls = response.xpath('//div[@class="post_item"]//div[@id="pnl_contentinfo"]//a//img/@src |\
                                    //div[@class="view clearfix"]//div[@class="vc_article"]//div[@class="va_con"]//a//img/@src'\
                                  ).extract()

       # 游记所在地
   #    scenicspot_locus = response.xpath('//div[@class="post-hd"]//div[@class="crumb"]//strong[last()-2]//a/text()').extract()
   #    scenicspot_locus = ''.join(scenicspot_locus).strip()[:-2]

       # 如果设置并开启了爬取的开始时间，则将早于开始时间的游记丢弃
       enable_start_crawling_time = mj_cf.get_str('mafengwo_spider','enable_start_crawling_time')
       if enable_start_crawling_time == 'True':
          start_crawling_time = mj_cf.get_str('mafengwo_spider','start_crawling_time')
          if travel_create_time < start_crawling_time:
             return None

       # 丢弃游记内容是空的
       if all_content == '':
         return None

       travel_item['travel_praisenum'] = travel_praisenum
       travel_item['travel_create_time'] = travel_create_time
       travel_item['travel_link'] = link
       travel_item['travel_title'] = title
       travel_item['travel_content'] = all_content
       travel_item['travel_viewnum'] = b_count
       travel_item['travel_commentnum'] = c_count
       travel_item['travel_time'] = travel_time
       travel_item['travel_people'] = travel_people
       travel_item['travel_cost'] = travel_cost
       travel_item['travel_type'] = travel_type
       travel_item['travel_days'] = travel_days
       travel_item['scenicspot_province'] = meta.get('scenicspot_province')
       travel_item['scenicspot_locus'] = meta.get('scenicspot_locus')
       travel_item['scenicspot_name'] = meta.get('scenicspot_name')
       travel_item['from_url'] = meta.get('from_url')

       return travel_item

