# -*- coding: utf-8 -*-

from zqtravel.items import TravelItem, ScenicspotItem
from zqtravel.lib.manufacture import ConfigMiaoJI
from zqtravel.lib.common import remove_str, get_data_dir_with

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy import log
import codecs

import scrapy
import re

mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class MafengwoProvinceSpider(scrapy.Spider):
    '''爬取蚂蜂窝的景点信息,按省抓取'''

    name = "mafengwo_province"
    allowed_domains = ["mafengwo.cn"]
    start_urls = mj_cf.get_starturls_from_province('mafengwo_province_spider',['pre_url', 'provinces'])

    rules = [
             Rule(LxmlLinkExtractor('/baike/'),
             callback='parse_locus_info',
             follow=True),
            ]

    def parse(self, response):
        '''省或直辖市的response.url => http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12703.html'''

        scenicspot_province = response.xpath('//div[@class="p-top clearfix"]//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][3]//span[@class="hd"]//text() | //div[@id="container"]//div[@class="row row-primary"]//div[@class="wrapper"]//div[@class="crumb"]//div[@class="item"][3]//span[@class="hd"]//text()').extract()
        scenicspot_province = ''.join(scenicspot_province).strip(u'省')

        province_id = response.url.split('/')[-1].split('.')[0]
        url_prefix = self.get_url_prefix(response, True)
        url_post = '/jd/' + province_id + '/'

        baike_info_url = ''.join([url_prefix, '/baike/info-', province_id, '.html'])
        # 获取省的信息
        yield Request(baike_info_url, callback=self.parse_locus_info, meta={'scenicspot_province':scenicspot_province})
        # 跳转到包含市的景点页面
        yield Request(url_prefix + url_post, callback=self.parse_cities, meta={'scenicspot_province':scenicspot_province})

    def parse_cities(self, response):
        '''省或直辖市的reponse.url => http://www.mafengwo.cn/jd/14407/'''

        # 城市链接
        city_href_list = response.xpath('//div[@class="content"]//div[@class="m-recList"]//div[@class="bd"]//dl[@class="clearfix"][2]//dd//@href').extract()
        city_name_list = response.xpath('//div[@class="content"]//div[@class="m-recList"]//div[@class="bd"]//dl[@class="clearfix"][2]//dd//a/h2/text()').extract()
        city_href_name_map = zip(city_href_list[1:], city_name_list)

        url_prefix = self.get_url_prefix(response, True)

        city_meta = response.meta

        # 非直辖市
        if len(city_href_list) >= 8: # 为了抓取充分，需要8个及以上城市的分类
          for city_href, city_name in city_href_name_map:
            city_id = city_href.split('/')[-2]
            baike_info_url = ''.join([url_prefix, '/baike/info-', city_id, '.html'])
            city_meta['scenicspot_locus'] = city_name
            yield Request(baike_info_url, callback=self.parse_locus_info,meta=city_meta)
            yield Request(url_prefix + city_href, callback=self.parse_city_scenicspot,meta=city_meta)
        # 直辖市
        else:
          city_id = response.url.split('/')[-2]
          baike_info_url = ''.join([url_prefix, '/baike/info-', city_id, '.html'])
          last_page_href = response.xpath('//div[@class="m-recList"]//div[@class="page-hotel"]/a[@class="ti last"][last()]/@href').extract()
          last_page_href = ''.join(last_page_href).strip()
          url = ''.join([response.url, last_page_href])
          city_meta['scenicspot_locus'] = city_meta.get('scenicspot_province','')
          # 获取城市的信息
          yield Request(baike_info_url, callback=self.parse_locus_info, meta=city_meta)
          # 抓取只有一个页面景点的城市
          if not last_page_href:
             scenicspots = self.parse_scenicspot_pages(response, one_page=True, meta=city_meta)
             for scenicspot in scenicspots:
                 yield scenicspot
          else: # 多个页面的景点
             yield Request(url, callback=self.parse_scenicspot_next_page, meta=city_meta)

    def parse_city_scenicspot(self, response):
        '''省下面的市或县的response.url => http://www.mafengwo.cn/jd/10163/'''       

        city_meta = response.meta 
        scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][4]//span[@class="hd"]//a/text()//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item "][4]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip()
        city_meta['city'] = scenicspot_locus
        last_page_href = response.xpath('//div[@class="m-recList"]//div[@class="page-hotel"]/a[@class="ti last"][last()]/@href').extract()
        last_page_href = ''.join(last_page_href).strip()
        url = ''.join([response.url, last_page_href])
        # 抓取只有一个页面景点的城市
        if not last_page_href:
           scenicspots = self.parse_scenicspot_pages(response, one_page=True, meta=city_meta)
           for scenicspot in scenicspots:
               yield scenicspot
        else: # 多个页面的景点
            yield Request(url, callback=self.parse_scenicspot_next_page, meta=city_meta)

    def parse_locus_info(self,response):
        '''获得省、市/县的相关信息'''

        scenicspot_item = ScenicspotItem()

        # 获取当前页面的省
        xpath_pre_without_blank = '//div[@class="wrapper"]//div[@class="crumb"]//'
        xpath_pre_with_blank = '//div[@class="wrapper"]//div[@class="crumb "]//'
        xpath_post_for_province = 'div[@class="item"][3]//span[@class="hd"]//a/text()'
        xpath_post_for_locus = 'div[@class="item"][4]//span[@class="hd"]//a/text()'
        scenicspot_province = response.xpath(xpath_pre_without_blank+xpath_post_for_province +'|'+ xpath_pre_with_blank+xpath_post_for_province).extract()
        scenicspot_province = remove_str(''.join(scenicspot_province).strip(),u'省')

        # 获取当前页面的市/县
        scenicspot_locus = response.xpath(xpath_pre_without_blank+xpath_post_for_locus +'|'+ xpath_pre_with_blank+xpath_post_for_locus).extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip(u'市')
        scenicspot_name = scenicspot_province
        
        # 省或直辖市的locus和scenicspot_name
        if u'攻略' in scenicspot_locus:
           scenicspot_locus = ''
        elif '' != scenicspot_locus:
           scenicspot_name = scenicspot_locus

        helpful_num = response.xpath('//div[@class="wrapper"]//div[@class="content"]//div[@class="m-title clearfix"]//span[@class="num-view"]/text()').extract()
        helpful_num = ''.join(helpful_num).strip()

        # 市、县相关信息 
        locus_info_title_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//h2/text()').extract()

        dict_title_to_content = {}
        content_index = 1
        for title in locus_info_title_list:
          xpath_without_p = '//div[@class="wrapper"]//div[@class="content"]//div[@class="m-txt"][' + str(content_index) + ']/text()'
          xpath_with_p = '//div[@class="wrapper"]//div[@class="content"]//div[@class="m-txt"][' + str(content_index) + ']//p/text()'
          content_list = response.xpath(xpath_without_p + '|' + xpath_with_p).extract()
          strip_content_list = [content.strip('\n\r\t ') for content in content_list]
          joined_content = '|'.join(strip_content_list)
          dict_title_to_content[title] = joined_content 
          content_index += 1

        scenicspot_item['scenicspot_intro'] = dict_title_to_content.get(u'简介')
        scenicspot_item['best_traveling_time'] = dict_title_to_content.get(u'最佳旅行时间')
        scenicspot_item['num_days'] = dict_title_to_content.get(u'建议游玩天数')
        scenicspot_item['weather'] = dict_title_to_content.get(u'当地气候')
        scenicspot_item['scenicspot_dressing'] = dict_title_to_content.get(u'穿衣指南')
        scenicspot_item['language'] = dict_title_to_content.get(u'语言')
        scenicspot_item['history'] = dict_title_to_content.get(u'历史')
        scenicspot_item['custom'] = dict_title_to_content.get(u'风俗禁忌')
        scenicspot_item['culture'] = dict_title_to_content.get(u'宗教与文化')
        scenicspot_item['helpful_num'] = helpful_num
        scenicspot_item['scenicspot_province'] = scenicspot_province 
        scenicspot_item['scenicspot_locus'] = scenicspot_locus
        scenicspot_item['scenicspot_name'] = scenicspot_name
        scenicspot_item['link'] = response.url

        if scenicspot_province:
          return scenicspot_item

    def parse_scenicspot_next_page(self, response):
        """获得城市景点的页地址, response.url => http://www.mafengwo.cn/jd/10065/0-0-0-0-0-46.html"""

        # 景点的总页数
        scenicspot_pages = response.xpath('//div[@class="m-recList"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的景点
        scenicspot_pages = int(''.join(scenicspot_pages).strip()) if len(scenicspot_pages) >= 1 else 1

        scenicspot_item = {}
        meta = response.meta
        # 景点所在省份
        scenicspot_province = meta.get('scenicspot_province')
        scenicspot_locus = ''
        if meta.get('scenicspot_locus'):
           scenicspot_locus = meta.get('scenicspot_locus')
        else:
           scenicspot_locus = meta.get('city')

        scenicspot_item['scenicspot_province'] = scenicspot_province.rstrip(u'省')
        if scenicspot_locus:
           scenicspot_item['scenicspot_locus'] = scenicspot_locus.rstrip(u'市')

        # 因为Scrapy的滤重，本页的景点也需要保证抓取到
        scenicspots = self.parse_scenicspot_pages(response, one_page=True, meta=scenicspot_item)
        for scenicspot in scenicspots:
           yield scenicspot

        # 景点每一页url
        url_prefix = response.url[:response.url.rfind('-')+1]
        for page_index in range(scenicspot_pages, 0, -1):
            url = ''.join([url_prefix, str(page_index), '.html'])
            yield Request(url, callback=self.parse_scenicspot_pages, meta={'scenicspot_item':scenicspot_item})
       
    def parse_scenicspot_pages(self, response, one_page=False, meta={}):
        '''获得每页中景点的地址'''
        '''one_page: True=>用于表明抓取只有一个页面景点的城市'''
        '''meta:     当抓取只有一个页面景点的城市时，保存省名和城市名'''

        scenicspot_meta = ScenicspotItem()
        # 一个页面时
        if one_page:
            scenicspot_meta['scenicspot_province'] = meta.get('scenicspot_province','')
            scenicspot_meta['scenicspot_locus'] = meta.get('scenicspot_locus','')
        else:
            scenicspot_meta['scenicspot_province'] = response.meta.get('scenicspot_item',{}).get('scenicspot_province','')
            scenicspot_meta['scenicspot_locus'] = response.meta.get('scenicspot_item',{}).get('scenicspot_locus','')
        # 一个页中的所有景点链接
        href_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//ul[@class="poi-list"]//li[@class="item clearfix"]//div[@class="title"]//@href').extract()
        # 一个页中的所有景点名称
        scenicspot_name_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//ul[@class="poi-list"]//li[@class="item clearfix"]//div[@class="title"]//a//text()').extract()
        href_scenicspot_name_group = zip(href_list, scenicspot_name_list)
    
        # 景点的等级
        scenicspot_grade_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//div[@class="m-recList"]//div[@class="bd"]//ul[@class="poi-list"]//li[@class="item clearfix"]//div[@class="grade"]/em/text()').extract()
        href_grade_group = dict(zip(href_list, scenicspot_grade_list))

        # 景点概况被认为有用的数量
        helpful_num_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//div[@class="m-recList"]//div[@class="bd"]//ul[@class="poi-list"]//li[@class="item clearfix"]//div[@class="grade"]/p/em/text()').extract()
        href_num_group = dict(zip(href_list, helpful_num_list))

        #scenicspot_meta = response.meta.get('scenicspot_item')
        province = scenicspot_meta.get('scenicspot_province')
        city = scenicspot_meta.get('scenicspot_locus', province)

        data_dir = get_data_dir_with(province)
        # 不获取游记的时候将游记连接写入文件
        youji_file = codecs.open('/'.join([data_dir, province + '_travel.urls']), "a", encoding='utf-8')

        re_href = re.compile('/poi/\d+\.html')

        url_prefix = self.get_url_prefix(response, splice_http=True)
        #if one_page:
          
        for href,scenicspot_name in href_scenicspot_name_group:
            m = re_href.match(href)
            if m:
                scenicspot_id = href[href.rfind('/')+1 : -5]
                scenicspot_info_url = ''.join([url_prefix, '/poi/',scenicspot_id, '.html'])
                scenicspot_youji_url = ''.join([url_prefix, '/poi/youji-',scenicspot_id, '.html'])
                youji_file.write(''.join([province,'|', city, '|', scenicspot_name, '|', scenicspot_youji_url, '\n']))
                youji_file.flush()

                scenicspot_meta['scenicspot_name'] = scenicspot_name.strip()
                scenicspot_meta['scenicspot_grade'] = href_grade_group.get(href).strip()
                scenicspot_meta['helpful_num'] = href_num_group.get(href).strip()
                scenicspot_meta['from_url'] = response.url
                yield Request(scenicspot_info_url, callback=self.parse_scenicspot_info_item, meta={'scenicspot_item':scenicspot_meta})

    def parse_scenicspot_info_item(self, response):
        '''解析景点信息'''

        scenicspot_item = response.meta['scenicspot_item']

        # 景点所市、县
        scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb crumb-white"]//div[@class="item"][4]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip(u'市')

        # 景点介绍
        scenicspot_intro = response.xpath('//div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dt//p//span//text()').extract()
        scenicspot_intro = ''.join(scenicspot_intro).strip()
        scenicspot_intro = re.sub(u'[“”‘’"\']', '', scenicspot_intro)

        # 景点的地址
        scenicspot_address = response.xpath('//div[@class="r-title"][1]/div/text()').extract()
        scenicspot_address = ''.join(scenicspot_address).strip()

        # 景点其他相关信息,如：电话，门票，开放时间等
        scenicspot_other_info_title_list = response.xpath('//div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dd//span[@class="label"]//text()').extract()

        dict_title_to_content = {}
        content_index = 1
        for title in scenicspot_other_info_title_list:
          xpath_without_a = '//div[@class="wrapper"]//dl[@class="intro"]//dd[' + str(content_index) + ']//p//text()'
          xpath_with_a = '//div[@class="wrapper"]//dl[@class="intro"]//dd[' + str(content_index) + ']//p//a//text()'
          content_list = response.xpath(xpath_without_a + '|' + xpath_with_a).extract()
          strip_content_list = [content.strip('\n\r\t ') for content in content_list]
          joined_content = '|'.join(strip_content_list)
          dict_title_to_content[title] = joined_content
          content_index += 1

        # 对景点的前6条评论
        scenicspot_comments_list = response.xpath('//div[@class="wrapper"]//ul[@class="rev-lists"]//li[position()<7]//p[@class="rev-txt"]//text()').extract()
        scenicspot_comments = '|'.join(scenicspot_comments_list)

        # 对景点的印象
        scenicspot_impression_list = response.xpath('//div[@class="wrapper"]//div[@class="rev-tags"]//strong/text()').extract()
        scenicspot_impression = '|'.join(scenicspot_impression_list)

        # 对景的名称
        name_xpath_pre = '//div[@class="banner wrapper"]//div[@class="cover"]//div[@class="s-title"]/'
        scenicspot_name = response.xpath(name_xpath_pre + 'h1/text()').extract()
        scenicspot_name = ''.join(scenicspot_name)

        if scenicspot_locus:
           scenicspot_item['scenicspot_locus'] = scenicspot_locus
        else:
           scenicspot_item['scenicspot_locus'] = scenicspot_item['scenicspot_province']
        scenicspot_name = re.sub(u'[“”‘’"\']', '', scenicspot_name)
        scenicspot_item['scenicspot_name'] = scenicspot_name
        scenicspot_item['scenicspot_intro'] = scenicspot_intro
        scenicspot_item['scenicspot_address'] = scenicspot_address
        scenicspot_item['scenicspot_comments'] = scenicspot_comments
        scenicspot_item['scenicspot_impression'] = scenicspot_impression
        scenicspot_item['traffic'] = dict_title_to_content.get(u'交通')
        scenicspot_item['scenicspot_tel'] = dict_title_to_content.get(u'电话')
        scenicspot_item['scenicspot_ticket'] = dict_title_to_content.get(u'门票')
        scenicspot_item['scenicspot_opentime'] = dict_title_to_content.get(u'开放时间')
        scenicspot_item['scenicspot_usedtime'] = dict_title_to_content.get(u'用时参考')
        scenicspot_item['scenicspot_webaddress'] = dict_title_to_content.get(u'网址')
        scenicspot_item['link'] = response.url
#        scenicspot_item['helpful_num'] = helpful_num
#        scenicspot_item['scenicspot_grade'] = scenicspot_grade
#        scenicspot_item['scenicspot_province'] = scenicspot_province
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
                   page_url_prefix = 'http://www.' + domain_name
                   break
        return page_url_prefix

