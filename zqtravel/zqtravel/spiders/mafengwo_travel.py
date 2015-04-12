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
             callback='parse_travel_next_pages',
             follow=True),
            ]

    def parse(self,response):
        travel_urls_root_dir = mj_cf.get_str('mafengwo_travel_spider','travel_urls_dir')
        travel_provinces = mj_cf.get_list('mafengwo_travel_spider','travel_provinces')
        if 'all' in travel_provinces:
           for dirpath, subdir_names, filenames in os.walk(travel_urls_root_dir):
               if filenames:
                  travel_urls_file = os.path.join(dirpath,filenames[0])
                  travel_urls = self.trigger_travel_url_from(travel_urls_file)
                  for travel_url in travel_urls:
                      yield travel_url
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
            travel_url = line_list[-1] 
            yield Request(travel_url, callback=self.parse_travel_next_pages)
        f_all_urls.close()

    def parse_travel_next_pages(self,response):
        """获得游记下一页地址"""

        # 游记的总页数
        travel_pages = response.xpath('//div[@class="wrapper"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的游记
        travel_pages = int(''.join(travel_pages).strip()) if len(travel_pages)>=1 else 0

        if not travel_pages:
          pass 
        else: # 游记每一页url
          travel_id = response.url[response.url.rfind('/')+1:-5]
          url_prefix = self.get_url_prefix(response, True)
          for page_index in range(1, travel_pages + 1):
            url = ''.join([url_prefix, '/yj/', travel_id, '/1-0-', str(page_index), '.html'])
            yield Request(url, callback=self.parse_travel_pages, meta=response.meta)

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

        tmp_item = response.meta.get('info_for_place')
        scenicspot_province = tmp_item.get('scenicspot_province')
        scenicspot_locus = tmp_item.get('scenicspot_locus')
        scenicspot_name = tmp_item.get('scenicspot_name')

        map_pre_xpath = '//div[@class="wrapper"]//div[@class="top-info clearfix"]//div[@class="crumb"]//'
        #scenicspot_name = response.xpath( map_pre_xpath + 'div[@class="item cur"]/strong/text()').extract()
        #scenicspot_name = ''.join(scenicspot_name).strip()

        # 所有游记链接
        youji_pre_xpath = '//div[@class="wrapper"]//div[@class="p-content"]//div[@class="m-post"]//ul[@class="post-list"]//li[@class="post-item clearfix"]//'
        href_list = response.xpath(youji_pre_xpath + 'h2[@class="post-title yahei"]/a/@href').extract()

        re_travel_href = re.compile('/i/\d+\.html')

        numview_numreply = response.xpath(youji_pre_xpath + 'span[@class="status"]/text()').extract()
        ## numview_numreply output format:
        ##  numview numreply numview  numreply ...
        ## [u'2824', u'13',  u'2462', u'27',   u'9594', u'24', u'2326', u'22', u'2345', u'7'] 
        ## 浏览数和评论数的对数跟页面中游记连接条数是一致的, 如：http://www.mafengwo.cn/yj/10219/2-0-42.html
        url_prefix = self.get_url_prefix(response, splice_http=True)
        travel_item = MafengwoItem()
        num_index = 0
        for href in href_list:
            m = re_travel_href.match(href)
            if m:
                numview = numview_numreply[num_index]
                numreply = numview_numreply[num_index+1]
                num_index += 2 # 以及上面numview_numreply的输出格式，每次的步数为2
                url = ''.join([url_prefix, href])
                #travel_item['travels_link'] = url 
                #travel_item['scenicspot_province'] =scenicspot_province
                #travel_item['scenicspot_locus'] = scenicspot_locus
                #travel_item['scenicspot_name'] = scenicspot_name
                #yield travel_item
                #return travel_item
               # 抓取游记内容的时候使用下面的yield回调
                meta_data = {"numreply":numreply, \
                             "numview":numview, \
                             "scenicspot_province":scenicspot_province, \
                             "scenicspot_locus":scenicspot_locus, \
                             "scenicspot_name":scenicspot_name \
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

       # 游记中的图片
       image_urls = response.xpath('//div[@class="post_item"]//div[@id="pnl_contentinfo"]//a//img/@src |\
                                    //div[@class="view clearfix"]//div[@class="vc_article"]//div[@class="va_con"]//a//img/@src'\
                                  ).extract()

       # 游记所在省
#       scenicspot_province = response.xpath('//div[@class="post-hd"]//div[@class="crumb"]//strong[2]//a/text()').extract()
 #      scenicspot_province = ''.join(scenicspot_locus).strip()[:-2]

       # 游记所在地
   #    scenicspot_locus = response.xpath('//div[@class="post-hd"]//div[@class="crumb"]//strong[last()-2]//a/text()').extract()
  #     scenicspot_locus = ''.join(scenicspot_locus).strip()[:-2]

       # 景点名称
    #   scenicspot_name = response.xpath('//div[@class="post-hd"]//div[@class="crumb"]//strong[last()-1]//a/text()').extract()
     #  scenicspot_name = ''.join(scenicspot_name).strip()[:-4]

       # 如果设置并开启了爬取的开始时间，则将早于开始时间的游记丢弃
       enable_start_crawling_time = mj_cf.get_str('mafengwo_spider','enable_start_crawling_time')
       if enable_start_crawling_time == 'True':
          start_crawling_time = mj_cf.get_str('mafengwo_spider','start_crawling_time')
          if travels_time < start_crawling_time:
             return None

       # 丢弃游记内容是空的
       if all_content == '':
         return None

       travel_item['travels_praisenum'] = travels_praisenum
       travel_item['travels_time'] = travels_time
       travel_item['travels_link'] = link
       travel_item['travels_title'] = title
       travel_item['travels_content'] = all_content
       travel_item['travels_viewnum'] = b_count
       travel_item['travels_commentnum'] = c_count
       travel_item['scenicspot_province'] = meta.get('scenicspot_province')
       travel_item['scenicspot_locus'] = meta.get('scenicspot_locus')
       travel_item['scenicspot_name'] = meta.get('scenicspot_name')
       #travel_item['image_urls'] = image_urls
       
#       image_item = ImageItem()

#       image_item['scenicspot_province'] = meta.get('scenicspot_province')
#       image_item['scenicspot_locus'] = meta.get('scenicspot_locus')
#       image_item['scenicspot_name'] = meta.get('scenicspot_name')
#       image_item['image_urls'] = image_urls
       # 如果从游记页不能取到景点，才使用总游记页中的获取到的景点
       #if '' == scenicspot_locus or '' == scenicspot_name:
        #  travel_item['scenicspot_locus'] = meta['scenicspot_locus'].rstrip(u'市') if meta['scenicspot_locus'] != u'中国' else meta['scenicspot_name'].rstrip(u'市')
         # travel_item['scenicspot_name'] = meta['scenicspot_name']
       #else:
        #  travel_item['scenicspot_locus'] = scenicspot_locus.rstrip(u'市')
         # travel_item['scenicspot_name'] = scenicspot_name

       return travel_item

