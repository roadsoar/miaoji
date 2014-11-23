# -*- coding: utf-8 -*-

from zqtravel.items import MafengwoItem, ScenicspotItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log
import codecs
import scrapy

import re

mj_cf = ConfigMiaoJI("./spider_settings.cfg")

class MafengwoSpider(CrawlSpider):
    '''爬取蚂蜂窝的游记和对应景点信息'''

    name = "mafengwo"
    allowed_domains = ["mafengwo.cn"]
    start_urls = mj_cf.get_starturls('mafengwo_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('/travel-scenic-spot/mafengwo/\d+.html'),
             callback='parse_travel_next_pages',
             follow=True),
            ]

    def parse_scenic_spots(self, response):
        self.parse(response)

    def parse(self,response):
        """获得景点"""

        # 得到页面中景点的href
        # 目前只抓取国内的,http://www.mafengwo.cn/mdd/页中的nav-item第2条对应国内
        # 如果不区分国内外，抓取全部的景点，则获取所有nav-item的href即可,xpath='//div[@class="nav-item"]//@href'
        scenicspot_hrefs = response.xpath('//div[@class="nav-item"][2]//@href').extract()

        url_prefix = self.get_url_prefix(response, True)

        # 景点url
        for href in scenicspot_hrefs:
            url = ''.join([url_prefix,href])
            yield Request(url, callback=self.parse_travel_next_pages)

    def parse_travel_next_pages(self,response):
        """获得游记下一页地址"""

        # 游记的总页数
        travel_pages = response.xpath('//div[@class="wrapper"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
          ## 如果没有获取到页数，则说明只有一页的游记
        travel_pages = int(''.join(travel_pages).strip()) if len(travel_pages) >= 1 else 1

        # 游记每一页url
        travel_id = response.url[response.url.rfind('/')+1:-5]
        url_prefix = self.get_url_prefix(response, True)
        for page_index in range(1, travel_pages + 1):
            url = ''.join([url_prefix, '/yj/', travel_id, '/2-0-', str(page_index), '.html'])
            yield Request(url, callback=self.parse_scenicspot_travel_pages)
        
        # 景点url
        scenicspot_page = response.xpath('//div[@class="nav-bg"]//div[@class="nav-inner"]//li[@class="nav-item"][1]//@href').extract()
        scenicspot_page = ''.join(scenicspot_page).strip()
        scenicspot_page_url = ''.join([url_prefix, scenicspot_page])
        yield Request(scenicspot_page_url, callback=self.parse_scenicspot_next_page)

    def parse_scenicspot_next_page(self, response):
        """获得景点下一页地址"""

        # 景点的总页数
        scenicspot_pages = response.xpath('//div[@class="m-recList"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
          ## 如果没有获取到页数，则说明只有一页的景点
        scenicspot_pages = int(''.join(scenicspot_pages).strip()) if len(scenicspot_pages) >= 1 else 1

        scenicspot_item = ScenicspotItem()
        # 景点所在省份
        scenicspot_province = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][last()-2]//span[@class="hd"]//a/text()').extract()
        if u'中国' in scenicspot_province:
           scenicspot_province = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][last()-1]//span[@class="hd"]//a/text()').extract()
        scenicspot_province = ''.join(scenicspot_province).strip()
        scenicspot_item['scenicspot_province'] = scenicspot_province

        # 景点每一页url
        url_prefix = response.url[:response.url.rfind('/')]
        for page_index in range(1, scenicspot_pages + 1):
            url = ''.join([url_prefix, '/0-0-0-0-0-', str(page_index), '.html'])
            yield Request(url, callback=self.parse_scenicspot_pages, meta={'scenicspot_item':scenicspot_item})

    def parse_scenicspot_pages(self, response):
        '''获得每个景点的地址'''

        # 所有景点链接
        href_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//li[@class="item clearfix"]//div[@class="title"]//@href').extract()
        re_href = re.compile('/poi/\d+\.html')

        url_prefix = self.get_url_prefix(response, splice_http=True)
        for href in href_list:
            m = re_href.match(href)
            if m:
                scenicspot_id = href[href.rfind('/')+1 : -5]
                url = ''.join([url_prefix, '/poi/info-',scenicspot_id, '.html#comment_header'])
                yield Request(url, callback=self.parse_scenicspot_info_item, meta=response.meta)

    def parse_scenicspot_info_item(self, response):
        '''解析景点信息'''

        scenicspot_item = response.meta['scenicspot_item']
        
        # 景点概况被认为有用的数量
        helpful_num = response.xpath('//div[@class="col-main"]//div[@class="poi-info poi-base tab-div"]//div[@class="hd"]//span[@class="s-view"]/text()').extract()
        helpful_num = ''.join(helpful_num).strip()

        # 景点所在地
        scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][last()-2]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip()
           # 如果还是获取到省，则获取下一级别的市县
        if scenicspot_item['scenicspot_province'] in scenicspot_locus or \
           scenicspot_locus in scenicspot_item['scenicspot_province'] or \
           scenicspot_locus == u'中国': # 如果获取到的是“中国”，重新获取
           scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][last()-1]//span[@class="hd"]//a/text()').extract()
           scenicspot_locus = ''.join(scenicspot_locus).strip()

        # 景点名称
        scenicspot_name = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item cur"]//strong/text()').extract()
        scenicspot_name = remove_str(''.join(scenicspot_name).strip(),'>')

        # 景点当地天气
        weather = response.xpath('//div[@class="top-info clearfix"]/div[@class="weather"]/text()').extract()
        weather = remove_str(remove_str(''.join(weather).strip(),u'：'),'\s+')

        # 景点门票价格
        scenicspot_ticket = response.xpath('//div[@class="m-box m-piao"]//div[@class="bd"]//li[@class="clearfix"]//span[@class="c3"]/text()').extract()
        scenicspot_ticket = u'￥' + ''.join(scenicspot_ticket).strip() + u'起' if scenicspot_ticket else ''

        # 景点简介相关信息 
        scenicspot_info_item_title = response.xpath('//div[@class="col-main"]//div[@class="poi-info poi-base tab-div"]//div[@class="bd"]//h3/text()').extract()
        scenicspot_info_item_content = response.xpath(\
                               '//div[@class="col-main"]//div[@class="poi-info poi-base tab-div"]//div[@class="bd"]//p/text() |\
                              //div[@class="col-main"]//div[@class="poi-info poi-base tab-div"]//div[@class="bd"]//p/a/text()' \
                                                     ).extract()
        # 生成title对应内容的字典，如：u'地址' : u'北京东城区景山前街4号'
        dict_title_to_content = dict(zip(scenicspot_info_item_title, scenicspot_info_item_content))

        scenicspot_item['scenicspot_intro'] = dict_title_to_content.get(u'简介')
        scenicspot_item['scenicspot_address'] = dict_title_to_content.get(u'地址')
        scenicspot_item['scenicspot_webaddress'] = dict_title_to_content.get(u'网址')
        scenicspot_item['scenicspot_tel'] = dict_title_to_content.get(u'电话')
        scenicspot_item['scenicspot_ticket'] = scenicspot_ticket
        scenicspot_item['helpful_num'] = helpful_num
        scenicspot_item['scenicspot_locus'] = scenicspot_locus
        scenicspot_item['scenicspot_name'] = scenicspot_name
        scenicspot_item['weather'] = weather
        scenicspot_item['link'] = response.url

        return scenicspot_item


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
                   page_url_prefix = 'http://' + domain_name
                   break
        return page_url_prefix

    def parse_scenicspot_travel_pages(self, response):
        """获取游记页地址"""

        # 景点所在地
        scenicspot_locus = response.xpath('//div[@class="p-top clearfix"]//div[@class="crumb"]//div[@class="item"][last()-1]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip()

        # 景点名称
        scenicspot_name = response.xpath('//div[@class="p-top clearfix"]//div[@class="crumb"]//div[@class="item"][last()]//span[@class="hd"]//a/text()').extract()
        scenicspot_name = ''.join(scenicspot_name).strip()

        # 所有游记链接
        href_list = response.xpath('//div[@class="post-list"]/ul/li[@class="post-item clearfix"]/h2[@class="post-title yahei"]//@href').extract()
        re_travel_href = re.compile('/i/\d+\.html')

        numview_numreply = response.xpath('//div[@class="post-list"]/ul/li[@class="post-item clearfix"]/span[@class="status"]/text()').extract()
        ## numview_numreply output format:
        ##  numview numreply numview  numreply ...
        ## [u'2824', u'13',  u'2462', u'27',   u'9594', u'24', u'2326', u'22', u'2345', u'7'] 
        ## 浏览数和评论数的对数跟页面中游记连接条数是一致的, 如：http://www.mafengwo.cn/yj/10219/2-0-42.html
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
                             "scenicspot_locus":scenicspot_locus, \
                             "scenicspot_name":scenicspot_name \
                            }
                yield Request(url, callback=self.parse_scenicspot_travel_item,meta=meta_data)


    def parse_scenicspot_travel_item(self, response):
       item = MafengwoItem()
       meta = response.meta

       # 游记链接
       link = response.url

       # 游记标题
       title = response.xpath('//div[@class="post-hd"]//div[@class="post_title clearfix"]/h1/text() |\
                              //div[@class="view_info"]//div[@class="vi_con"]/h1/text()' \
                             ).extract()
       title = remove_str(title[0],'[\r\n\s]') if len(title) >= 1 else ''

       # 游记发布时间
       travels_time = response.xpath('//div[@class="post_item"]//div[@class="tools no-bg"]//div[@class="fl"]//span[@class="date"]/text() |\
                                      //div[@class="view clearfix"]//div[@class="vc_title clearfix"]//div[@class="vc_time"]/span[@class="time"]/text()' \
                                    ).extract()
       travels_time = ''.join(travels_time).strip()

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
       travels_praisenum = response.xpath('//div[@class="post-hd"]//div[@class="bar_share"]/div[@class="post-up"]/div[@class="num"]/text() |\
                                           //div[@class="view clearfix"]//div[@class="ding"]/strong/text()' \
                                         ).extract()
       travels_praisenum = ''.join(travels_praisenum).strip()

       # 景点所在地
       scenicspot_locus = response.xpath('//div[@class="post-hd"]//div[@class="crumb"]//strong[last()-2]//a/text()').extract()
       scenicspot_locus = ''.join(scenicspot_locus).strip()[:-2]

       # 景点名称
       scenicspot_name = response.xpath('//div[@class="post-hd"]//div[@class="crumb"]//strong[last()-1]//a/text()').extract()
       scenicspot_name = ''.join(scenicspot_name).strip()[:-4]

       # 如果设置并开启了爬取的开始时间，则将早于开始时间的游记丢弃
       enable_start_crawling_time = mj_cf.get_str('mafengwo_spider','enable_start_crawling_time')
       if enable_start_crawling_time == 'True':
          start_crawling_time = mj_cf.get_str('mafengwo_spider','start_crawling_time')
          if travels_time < start_crawling_time:
             return None

       # 丢弃游记内容是空的
       if all_content == '':
         return None

       item['travels_praisenum'] = travels_praisenum
       item['travels_time'] = travels_time
       item['travels_link'] = link
       item['travels_title'] = title
       item['travels_content'] = all_content
       item['travels_viewnum'] = b_count
       item['travels_commentnum'] = c_count
       
       # 如果从游记页不能取到景点，才使用总游记页中的获取到的景点
       if '' == scenicspot_locus or '' == scenicspot_name:
          item['scenicspot_locus'] = meta['scenicspot_locus'] if meta['scenicspot_locus'] != u'中国' else meta['scenicspot_name']
          item['scenicspot_name'] = meta['scenicspot_name']
       else:
          item['scenicspot_locus'] = scenicspot_locus
          item['scenicspot_name'] = scenicspot_name

       return item

