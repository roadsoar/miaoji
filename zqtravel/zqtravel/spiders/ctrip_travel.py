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


mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class CtripTravelSpider(scrapy.Spider):
    '''爬取携程的游记'''

    name = "ctrip_travel"
    allowed_domains = ["you.ctrip.com"]
    start_urls = mj_cf.get_starturls('ctrip_travel_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('/travels/'),
             callback='parse_travel_next_pages',
             follow=True),
            ]

    def parse(self,response):
        travel_urls_root_dir = mj_cf.get_str('ctrip_travel_spider','travel_urls_dir')
        travel_provinces = mj_cf.get_list('ctrip_travel_spider','travel_provinces')
        # 爬取所有省份
        if not travel_provinces:
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
            scenicspot_info = {}
            scenicspot_info['scenicspot_province'] = scenicspot_province
            scenicspot_info['scenicspot_locus'] = scenicspot_locus
            scenicspot_info['scenicspot_name'] = ''
            travel_url = line_list[-1].strip()
            yield Request(travel_url, callback=self.parse_travel_next_pages, meta={'scenicspot_info':scenicspot_info})
        f_all_urls.close()

    def parse_travel_next_pages(self,response):
        """获得游记下一页地址, response.url => http://you.ctrip.com/travels/lijiang32/.html """

        # 游记的总页数
        page_xpath = '//div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]//div[@class="pager_v1"]//%s'
        travel_pages = response.xpath(page_xpath % 'span/b/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的游记
        travel_pages = int(''.join(travel_pages).strip()) if len(travel_pages)>=1 else 0

        # 为了抓取第一页面,直接调用获取游记页地址方法=>parse_travel_pages
        travel_urls = self.parse_travel_pages(response)
        for travel_url in travel_urls:
            yield travel_url

        fetch_js = mj_cf.get_bool('ctrip_travel_spider','fetch_js')
        # 抓取的动态网页
        if fetch_js:
           for page_index in range(travel_pages, 1, -1):
               url = re.sub(r'\d+\)',str(page_index)+')',js_travel_href)
               yield Request(url, callback=self.parse_travel_pages, meta=response.meta)
        # 非动态网页
        else:
           page_xpath = '//div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]//div[@class="pager_v1"]//%s'
           template_href = response.xpath(page_xpath % 'a[@class="nextpage"]/@href').extract()
           template_href = ''.join(template_href)
           pre_url = get_url_prefix(response, self.allowed_domains)
           for page_index in range(travel_pages, 1, -1):
               href = re.sub(r'\d+\.html', str(page_index)+'.html', template_href)
               url = '%s%s' % (pre_url, href)
               yield Request(url, callback=self.parse_travel_pages, meta=response.meta)

    def parse_travel_pages(self, response):
        """获取游记页地址, response.url => http://you.ctrip.com/travels/lijiang32/t3-p3.html"""

        # 所有游记链接
        sel_xpath ='//div[@class="content cf"]//div[@class="normalbox"]//div[@class="journalslist cf"]//a[@class="journal-item cf"]'
        sel_as = response.xpath(sel_xpath)

        tmp_item = response.meta.get('scenicspot_info')
        scenicspot_province = tmp_item.get('scenicspot_province')
        scenicspot_locus = tmp_item.get('scenicspot_locus')
        scenicspot_name = tmp_item.get('scenicspot_name')

        url_prefix = get_url_prefix(response, self.allowed_domains)
        for sel_a in sel_as:
            href = sel_a.xpath('@href').extract()
            href = ''.join(href)
            numview = sel_a.xpath('.//ul//i[@class="numview"]/text()').extract()
            numview = ''.join(numview).strip()
            numcomment = sel_a.xpath('.//ul//i[@class="numreply"]/text()').extract()
            numcomment = ''.join(numcomment).strip()
            numpraise = sel_a.xpath('.//ul//i[@class="want"]/text()').extract()
            numpraise = ''.join(numpraise).strip()
            url = '%s%s' % (url_prefix, href)
            meta_data = {"numcomment":numcomment, \
               "numview":numview, \
               "numpraise":numpraise, \
               "scenicspot_province":scenicspot_province, \
               "scenicspot_locus":scenicspot_locus, \
               "scenicspot_name":scenicspot_name, \
               "from_url":response.url \
                            }
            yield Request(url, callback=self.parse_scenicspot_travel_item,meta=meta_data)

    def parse_scenicspot_travel_item(self, response):

       travel_item = TravelItem()
       meta = response.meta

       # 游记链接
       link = response.url

       # 游记标题
       title = response.xpath('//div[@class="content ctd_head_box"]//div[@class="ctd_head_left"]/h2/text()').extract()
       title = ''.join(title).strip()
       title = re.sub(u'[“”‘’"\']', '', title)

       info_xpath = '//div[@class="content cf"]//div[@class="ctd_content"]//div[@class="ctd_content_controls cf"]//%s'
       # 游记中涉及的景点
       scenicspot_in_trip = response.xpath(info_xpath % 'div[@class="author_poi"]//dd//a/@title').extract()

       infos = ''.join(response.xpath(info_xpath % 'span').extract())
       # 游玩的时间
       rs_time = re.match(r'.*times.*?i>(.*?)</span',  infos)
       travel_time = rs_time.group(1).strip() if rs_time else ''
       # 游玩的人数
       rs_people = re.match(r'.*whos.*?i>(.*?)</span',  infos)
       travel_people = rs_people.group(1).strip() if rs_people else ''
       # 游玩的天数
       rs_days = re.match(r'.*days.*?i>(.*?)</span',  infos)
       travel_days = rs_days.group(1).strip() if rs_days else ''
       # 游玩的方式 eg:骑行，自由行等 
       rs_type = re.match(r'.*plays.*?i>(.*?)</span',  infos)
       travel_type = rs_type.group(1).strip() if rs_type else ''
       # 人均费用
       rs_cost = re.match(r'.*costs.*?i>(.*?)</span',  infos)
       travel_cost = rs_cost.group(1).strip() if rs_cost else ''

       content_xpath = '//div[@class="content cf"]//div[@class="ctd_content"]//%s'
       content_xpath2 = '//div[@class="content cf"]//div[@class="ctd_content wtd_content"]//%s'
       # 游记创建时间
       travel_create_time = response.xpath(content_xpath % 'h3//text()').extract()
       travel_create_time = ''.join(travel_create_time).strip()
       travel_create_time = ' '.join(travel_create_time.split()[-2:])

       # 游记内容
       all_content = response.xpath(content_xpath % 'p//text()|'\
                                   + content_xpath % 'p//strong/text()|'\
                                   + content_xpath % 'p//a/text()' \
                                   ).extract()
       all_content = remove_str(remove_str(''.join(all_content).strip()),'\s{2,}')
       all_content = re.sub(u'[“”‘’"\']', '', all_content)

       # 游记的评论
       comment_xpath ='//div[@class="content cf"]//div[@class="ctd_comments"]//div[@id="replyboxid"]//div[@class="ctd_comments_box cf"]'
       sel_comments = response.xpath(comment_xpath)
       travel_comments = []
       for sel_comment in sel_comments:
           comments = sel_comment.xpath('.//div[@class="textarea_box fr"]//p//text()').extract()
           comments = ''.join(comments).strip()
           travel_comments.append(comments)
       travel_comments = '|'.join(travel_comments)

       # 游记浏览数
       numview = meta.get('numview','')

       # 游记评论数
       commentnum = meta.get('numcomment','')

       # 游记被赞或顶的数量
       travel_praisenum = meta.get('numpraise','')

       # 游记中的图片
       image_urls = response.xpath(content_xpath % 'div[@class="img"]//a//@href |' + content_xpath2 % 'div[@class="img"]//a//@href').extract()

       # 如果设置并开启了爬取的开始时间，则将早于开始时间的游记丢弃
       enable_start_crawling_time = mj_cf.get_str('mafengwo_spider','enable_start_crawling_time')
       if enable_start_crawling_time == 'True':
          start_crawling_time = mj_cf.get_str('mafengwo_spider','start_crawling_time')
          if travel_create_time < start_crawling_time:
             return None

       # 丢弃游记内容是空的
       if all_content == '':
         return None
        
       # 丢弃不包含图片的游记
       if not image_urls:
         return None
      
       # 丢弃3年以前或不符合抓取规则的游记
       if not fetch_travel(travel_create_time, numview):
          return None

       try:
          image_num = mj_cf.get_int('mafengwo_travel_spider','image_num_every_travel')
          for image_url in image_urls:
             if not re.match(r'.*\d+x\d+\.gif',image_url): # 过滤超小文件
                travel_item['image_urls'].append(image_url)
             if len(travel_item['image_urls']) > image_num:
                break
       except: # 如果没有设置，或设置错误则抓取游记中的全部图片
          image_num = None

       travel_item['travel_praisenum'] = travel_praisenum
       travel_item['travel_create_time'] = travel_create_time
       travel_item['travel_link'] = link
       travel_item['travel_title'] = title
       travel_item['travel_content'] = all_content
       travel_item['travel_viewnum'] = numview
       travel_item['travel_commentnum'] = commentnum
       travel_item['travel_time'] = travel_time
       travel_item['travel_people'] = travel_people
       travel_item['travel_cost'] = travel_cost
       travel_item['travel_type'] = travel_type
       travel_item['travel_days'] = travel_days
       travel_item['scenicspot_province'] = meta.get('scenicspot_province')
       travel_item['scenicspot_locus'] = meta.get('scenicspot_locus')
       scenicspot_name = re.sub(u'[“”‘’"\']', '', meta.get('scenicspot_name'))
       travel_item['scenicspot_name'] = scenicspot_name
       travel_item['from_url'] = meta.get('from_url')
       #travel_item['image_urls'] = image_urls[:image_num]
       travel_item['travel_comments'] = travel_comments
       travel_item['scenicspot_in_trip'] = scenicspot_in_trip

       return travel_item
