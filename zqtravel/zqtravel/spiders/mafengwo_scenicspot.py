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
import re

mj_cf = ConfigMiaoJI("./spider_settings.cfg")
class MafengwoScenicspotSpider(scrapy.Spider):
    '''爬取蚂蜂窝的游记和对应景点信息'''
    name = "mafengwo_scenicspot"
    allowed_domains = ["mafengwo.cn"]
    start_urls = mj_cf.get_starturls('mafengwo_scenicspot_spider','start_urls')

    rules = [
             Rule(LxmlLinkExtractor('/travel-scenic-spot/mafengwo/'),
             callback='parse_scenic_spots',
             follow=True),
             Rule(LxmlLinkExtractor('/poi/\d+.html'),
             callback='parse_scenic_spots',
             follow=True),
             Rule(LxmlLinkExtractor('/i/\d+.html'),
             callback='parse_scenic_spots',
             follow=True),
            ]

    def parse_scenic_spots(self, response):
        self.parse(response)

    def parse(self,response):
        """获得景点"""

        # 得到页面中景点的href
        # 目前只抓取国内的
        province_hrefs = response.xpath('//div[@id="Mcon"]//div[@class="content"]//div[@class="MddLi"]//dl[2]//dd//@href').extract()
        province_names= response.xpath('//div[@id="Mcon"]//div[@class="content"]//div[@class="MddLi"]//dl[2]//dd//a/text()').extract()
        href_to_name = zip(province_hrefs,province_names)

        url_prefix = self.get_url_prefix(response, True)

        disallow_cities = mj_cf.get_dict('mafengwo_spider','disallow_cities').values()
        # 省url
        for href,name in href_to_name:
            province_id = href.split('=')[1]
            if province_id not in disallow_cities:
               province_url = ''.join([url_prefix,'/travel-scenic-spot/mafengwo/', province_id, '.html'])
               yield Request(province_url, callback=self.parse_province_and_scenicspot, meta={'province_name':name.strip()})
    
    def parse_province_and_scenicspot(self, response):
        '''省或直辖市的response.url => http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10035.html'''

        province_info_url = response.xpath('//div[@class="nav-bg"]//div[@class="nav-inner"]//li[@class="nav-item nav-drop"]/a[@class="drop-hd"]/@href').extract()
        province_info_url = ''.join(province_info_url).strip()

        scenicspot_url = response.xpath('//div[@class="nav-bg"]//div[@class="nav-inner"]//li[@class="nav-item"][1]//@href').extract()
        scenicspot_url = ''.join(scenicspot_url).strip()

        url_prefix = self.get_url_prefix(response, True)

        yield Request(url_prefix + province_info_url, callback=self.parse_locus_info, meta=response.meta)
        yield Request(url_prefix + scenicspot_url, callback=self.parse_cities, meta=response.meta)

    def parse_cities(self, response):
        '''省或直辖市的reponse.url => http://www.mafengwo.cn/jd/14407/gonglve.html'''

        # 非直辖市
        city_href_list = response.xpath('//div[@class="content"]//div[@class="m-recList"]//div[@class="bd"]//dl[@class="clearfix"][2]//dd//@href').extract()
        city_name_list = response.xpath('//div[@class="content"]//div[@class="m-recList"]//div[@class="bd"]//dl[@class="clearfix"][2]//dd//a/h2/text()').extract()
        city_href_name_map = zip(city_href_list[1:], city_name_list)
        # 直辖市
        self_governed_city_href = response.xpath('//div[@id="container"]//div[@class="row row-allPlace row-bg"]//div[@class="wrapper"]//div[@class="list"]//ul[@class="clearfix"]//li//@href').extract()

        url_prefix = self.get_url_prefix(response, True)

        city_meta = response.meta

        # 非直辖市
        for city_href, city_name in city_href_name_map:
            city_id = city_href.split('/')[-2]
            baike_info_url = ''.join([url_prefix, '/baike/info-', city_id, '.html'])
            city_meta['scenicspot_locus'] = city_name
            yield Request(baike_info_url, callback=self.parse_locus_info,meta=city_meta)
            yield Request(url_prefix + city_href, callback=self.parse_city_scenicspot,meta=city_meta)

        # 直辖市
        if self_governed_city_href:
          city_id = href.split('/')[-2]
          baike_info_url = ''.join([url_prefix, '/baike/info-', city_id, '.html'])
          yield Request(baike_info_url, callback=self.parse_locus_info, meta=city_meta)
          # 直辖市的景点
          for href in self_governed_city_href:
            scenicspot_locus = response.xpath('//div[@id="container"]//div[@class="row row-primary"]//div[@class="wrapper"]//div[@class="crumb"]//div[@class="item"]//span[@class="hd"]//a/text()').extract()
            scenicspot_locus = ''.join(scenicspot_locus).strip()
            city_meta['scenicspot_locus'] = scenicspot_locus
            yield Request(url_prefix + href, callback=self.parse_scenicspot_info_item, meta=city_meta)
            # 获取游记时调用
            #youji_url = ''.join([url_prefix, '/poi/youji-', city_id, '.html'])
            #yield Request(youji_href, callback=self.parse_scenicspot_travel_pages, meta=city_meta)

    def parse_city_scenicspot(self, response):
        '''省下面的市或县的response.url => http://www.mafengwo.cn/jd/10163/'''       

        city_meta = response.meta 
        scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][4]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip()
        city_meta['city'] = scenicspot_locus
        first_href = response.xpath('//div[@class="m-recList"]//div[@class="page-hotel"]/a[@class="ti"][1]/@href').extract()
        first_href = ''.join(first_href).strip()
        url = ''.join([response.url, first_href])
        yield Request(url, callback=self.parse_scenicspot_next_page, meta=city_meta)

    def parse_locus_info(self,response):
        '''获得省、市/县的相关信息'''

        scenicspot_item = ScenicspotItem()

        # 获取当前页面的省
        scenicspot_province = response.xpath('//div[@class="wrapper"]//div[@class="crumb "]//div[@class="item"][3]//span[@class="hd"]//a/text()').extract()
        scenicspot_province = remove_str(''.join(scenicspot_province).strip(),u'省')

        # 获取当前页面的市/县
        scenicspot_locus = response.xpath('//div[@class="wrapper"]//div[@class="crumb "]//div[@class="item"][4]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = remove_str(''.join(scenicspot_locus).strip(),u'市')

        scenicspot_name = scenicspot_locus
        
        # 省和市相同,则获取的是直辖市
        if '' == scenicspot_locus:
           scenicspot_locus = scenicspot_province
           scenicspot_name = scenicspot_province
  
        # 市/县名包含'攻略'，则获取的是省信息
        if u'攻略' in scenicspot_locus:
           scenicspot_locus = ''
           scenicspot_name = scenicspot_province

        helpful_num = response.xpath('//div[@class="wrapper"]//div[@class="content"]//div[@class="m-title clearfix"]//span[@class="num-view"]/text()').extract()
        helpful_num = ''.join(helpful_num).strip()

        # 景点相关信息 
        locus_info_title_list = response.xpath('//div[@class="wrapper"]//div[@class="content"]//h2/text()').extract()

        dict_title_to_content = {}
        content_index = 1
        for title in locus_info_title_list:
          xpath_without_p = '//div[@class="wrapper"]//div[@class="content"]//div[@class="m-txt"][' + str(content_index ) + ']/text()'
          xpath_with_p = '//div[@class="wrapper"]//div[@class="content"]//div[@class="m-txt"][' + str(content_index ) + ']//p/text()'
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
        scenicspot_item['helpful_num'] = helpful_num
        scenicspot_item['scenicspot_province'] = scenicspot_province 
        scenicspot_item['scenicspot_locus'] = scenicspot_locus
        scenicspot_item['scenicspot_name'] = scenicspot_name
        scenicspot_item['link'] = response.url


        return scenicspot_item

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
            url = ''.join([url_prefix, '/yj/', travel_id, '/1-0-', str(page_index), '.html'])
            #yield Request(url, callback=self.parse_scenicspot_travel_pages, meta=response.meta)
        
        # 景点url
        scenicspot_page = response.xpath('//div[@class="nav-bg"]//div[@class="nav-inner"]//li[@class="nav-item"][1]//@href').extract()
        scenicspot_page = ''.join(scenicspot_page).strip()
        scenicspot_page_url = ''.join([url_prefix, scenicspot_page])
        #yield Request(scenicspot_page_url, callback=self.parse_scenicspot_next_page)

    def parse_scenicspot_next_page(self, response):
        """获得城市景点的页地址, response.url => http://www.mafengwo.cn/jd/10163/0-0-0-0-0-2.html"""

        # 景点的总页数
        scenicspot_pages = response.xpath('//div[@class="m-recList"]//div[@class="page-hotel"]/span[@class="count"]/span[1]/text()').extract()
        ## 如果没有获取到页数，则说明只有一页的景点
        scenicspot_pages = int(''.join(scenicspot_pages).strip()) if len(scenicspot_pages) >= 1 else 1

        scenicspot_item = ScenicspotItem()
        meta = response.meta
        # 景点所在省份
        scenicspot_province = meta.get('province_name') #response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][last()-2]//span[@class="hd"]//a/text()').extract()
#        if u'中国' in scenicspot_province:
#           scenicspot_province = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][last()-1]//span[@class="hd"]//a/text()').extract()
#        scenicspot_province = ''.join(scenicspot_province).strip()
        #scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb"]//div[@class="item"][4]//span[@class="hd"]//a/text()').extract()
        #scenicspot_locus = ''.join(scenicspot_locus).strip()
        scenicspot_locus = ''
        if meta.get('scenicspot_locus'):
           scenicspot_locus = meta.get('scenicspot_locus')
        else:
           scenicspot_locus = meta.get('city')

        scenicspot_item['scenicspot_province'] = scenicspot_province.rstrip(u'省')
        scenicspot_item['scenicspot_locus'] = scenicspot_locus.rstrip(u'市')

        # 景点每一页url
        url_prefix = response.url[:response.url.rfind('-')+1]
        for page_index in range(1, scenicspot_pages + 1):
            url = ''.join([url_prefix, str(page_index), '.html'])
            yield Request(url, callback=self.parse_scenicspot_pages, meta={'scenicspot_item':scenicspot_item})

    def parse_scenicspot_pages(self, response):
        '''获得每页景点的地址'''

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

        scenicspot_meta = response.meta.get('scenicspot_item')
        city = scenicspot_meta.get('scenicspot_locus')
        province = scenicspot_meta.get('scenicspot_province')

        data_dir = get_data_dir_with(province)
        # 不获取游记的时候将游记连接写入文件
        youji_file = codecs.open('/'.join([data_dir, province + '_travel.urls']), "a", encoding='utf-8')

        re_href = re.compile('/poi/\d+\.html')

        url_prefix = self.get_url_prefix(response, splice_http=True)
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
                yield Request(scenicspot_info_url, callback=self.parse_scenicspot_info_item, meta={'scenicspot_item':scenicspot_meta})
            # 获取游记的时候调用
            #    yield Request(scenicspot_youji_url, callback=self.parse_scenicspot_travel_pages, meta=response.meta)

    def parse_scenicspot_info_item(self, response):
        '''解析景点信息'''

        scenicspot_item = response.meta['scenicspot_item']

        # 景点所在地
        scenicspot_locus = response.xpath('//div[@class="top-info clearfix"]//div[@class="crumb crumb-white"]//div[@class="item"][4]//span[@class="hd"]//a/text()').extract()
        scenicspot_locus = ''.join(scenicspot_locus).strip()

        # 景点介绍
        scenicspot_intro = response.xpath('//div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dt//div[@class="simrows active"]//p//span//text()').extract()
        scenicspot_intro = ''.join(scenicspot_intro).strip()

        # 景点的地址
        scenicspot_address = response.xpath('//div[@class="row row-location row-bg"]//div[@class="wrapper"]//div[@class="r-title"]//text()').extract()
        scenicspot_address = ': '.join(scenicspot_address).strip()

        # 景点其他相关信息,如：电话，门票，开放时间等
        scenicspot_other_info_title = response.xpath('//div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dd//span[@class="label"]//text()').extract()
        scenicspot_other_info_content = response.xpath('//div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dd//div[@class="simrows active"]//p//span//text()|\
                                                        //div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dd//div[@class="simrows"]//p//span//text()|\
                                                        //div[@class="row row-overview"]//div[@class="wrapper"]//dl[@class="intro"]//dd//p//text()'\
                                                      ).extract()
        # 生成title对应内容的字典，如：u'地址' : u'北京东城区景山前街4号'
        dict_title_to_content = dict(zip(scenicspot_other_info_title, scenicspot_other_info_content))

        # 对景点的前6条评论
        scenicspot_comments_list = response.xpath('//div[@class="row row-reviews row-bg"]//div[@class="wrapper"]//ul[@class="rev-lists"]//li[position()<7]//p[@class="rev-txt"]//text()').extract()
        scenicspot_comments = '|'.join(scenicspot_comments_list)

        # 对景点的印象
        scenicspot_impression_list = response.xpath('//div[@class="row row-reviews row-bg"]//div[@class="wrapper"]//div[@class="rev-tags"]//ul//li[@class="filter-word"]//a//strong//text()').extract()
        scenicspot_impression = '|'.join(scenicspot_impression_list)

        # 避免title和content错位
#        title_item_num = len(scenicspot_info_item_title)
#        content_item_num = len(scenicspot_info_item_content)
#        re_tel = re.compile('\d{2,}-?\d{6,}')
#        while content_item_num > title_item_num and not re_tel.match(scenicspot_info_item_content[2]) and content_item_num > 2:
#           content = []
#           content.append(''.join(scenicspot_info_item_content[:2]))
#           content.extend(scenicspot_info_item_content[2:])
#           scenicspot_info_item_content = content
#           content_item_num = len(scenicspot_info_item_content)

        scenicspot_item['scenicspot_intro'] = scenicspot_intro
        scenicspot_item['scenicspot_address'] = scenicspot_address
        scenicspot_item['scenicspot_comments'] = scenicspot_comments
        scenicspot_item['scenicspot_impression'] = scenicspot_impression
        scenicspot_item['traffic'] = dict_title_to_content.get(u'交通')
        scenicspot_item['scenicspot_tel'] = dict_title_to_content.get(u'电话')
        scenicspot_item['scenicspot_ticket'] = dict_title_to_content.get(u'门票')
        scenicspot_item['scenicspot_opentime'] = dict_title_to_content.get(u'开放时间')
        scenicspot_item['scenicspot_usedtime'] = dict_title_to_content.get(u'用时参考')
        scenicspot_item['link'] = response.url
#        scenicspot_item['scenicspot_locus'] = scenicspot_locus
#        scenicspot_item['helpful_num'] = helpful_num
#        scenicspot_item['scenicspot_name'] = scenicspot_name
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

    def parse_scenicspot_travel_pages(self, response):
        """获取游记页地址"""

        # 景点所在地
        #scenicspot_locus = response.xpath('//div[@class="p-top clearfix"]//div[@class="crumb"]//div[@class="item"][last()-1]//span[@class="hd"]//a/text()').extract()
        #scenicspot_locus = ''.join(scenicspot_locus).strip()

        tmp_item = response.meta.get('scenicspot_item')
        scenicspot_province = tmp_item.get('scenicspot_province')
        scenicspot_locus = tmp_item.get('scenicspot_locus')

        # 景点名称
        #scenicspot_name = response.xpath('//div[@class="p-top clearfix"]//div[@class="crumb"]//div[@class="item cur"]//strong/text()').extract()
        map_pre_xpath = '//div[@class="wrapper"]//div[@class="top-info clearfix"]//div[@class="crumb"]//'
        scenicspot_name = response.xpath( map_pre_xpath + 'div[@class="item cur"]/strong/text()').extract()
        scenicspot_name = ''.join(scenicspot_name).strip()

        # 所有游记链接
       # href_list = response.xpath('//div[@class="post-list"]/ul/li[@class="post-item clearfix"]/h2[@class="post-title yahei"]//@href').extract()
        youji_pre_xpath = '//div[@class="wrapper"]//div[@class="col-main"]//div[@class="poi-travelnote tab-div"]//ul[@class="post-list"]//li[@class="post-item clearfix"]//'
        href_list = response.xpath(youji_pre_xpath + 'h2[@class="post-title yahei"]/a/@href').extract()
        href_title_list = response.xpath(youji_pre_xpath + 'h2[@class="post-title yahei"]/a/text()').extract()
        href_title_group = zip(href_list, href_title_list)

        re_travel_href = re.compile('/i/\d+\.html')

        numview_numreply = response.xpath(youji_pre_xpath + 'span[@class="status"]/text()').extract()
        ## numview_numreply output format:
        ##  numview numreply numview  numreply ...
        ## [u'2824', u'13',  u'2462', u'27',   u'9594', u'24', u'2326', u'22', u'2345', u'7'] 
        ## 浏览数和评论数的对数跟页面中游记连接条数是一致的, 如：http://www.mafengwo.cn/yj/10219/2-0-42.html
        url_prefix = self.get_url_prefix(response, splice_http=True)
        travel_item = MafengwoItem()
        num_index = 0
        for href, title in href_title_group:
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

