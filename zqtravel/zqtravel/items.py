# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class CtripItem(Item):
    '''携程的游记条目'''

    travel_link = Field()     # 游记链接
    travel_title = Field()    # 游记标题
    travel_content = Field()  # 游记内容
    browse_count = Field()    # 游记浏览数量
    comment_count = Field()   # 游记评论数量
#    comment_content = Field() # 游记评论内容

class MafengwoItem(Item):
    '''蚂蜂窝的游记条目'''

    travels_praisenum = Field()        # 游记被赞的数量
    travels_viewnum = Field()          # 游记的浏览数量
    travels_commentnum = Field()       # 游记的评论数量
    travels_title = Field()            # 游记的标题
    travels_time = Field()             # 游记创建的时间
    travels_link = Field()             # 游记的链接
    travels_content = Field()          # 游记的内容
    scenicspot_province = Field()      # 景点所在地，即所在的省
    scenicspot_name = Field()          # 景点名称
    scenicspot_locus = Field()         # 景点所在地，即所在的省/市/县
                                       # scenicspot_name和scenicspot_locus，是为了区分游记文件的路径
    image_urls = Field()
    images = Field()

class ImageItem(Item):
    '''图片条目'''
    scenicspot_province = Field()      # 景点所在地，即所在的省
    scenicspot_name = Field()          # 景点名称
    scenicspot_locus = Field()         # 景点所在地，即所在的省/市/县
                                       # scenicspot_name和scenicspot_locus，是为了区分游记文件的路径
    image_urls = Field()
    images = Field()

class ScenicspotItem(Item):
    '''景点条目'''

    scenicspot_locus = Field()         # 景点所在地，即所在的市/县
    scenicspot_province = Field()      # 景点所在地，即所在的省
    link = Field()                     # 景点简介的链接
    area = Field()                     # 
    abstract = Field()                 # 省市概况
    num_days = Field()                 # 建议游玩天数
    weather = Field()                  # 穿衣指南
    language = Field()                 # 地方语言特色简介
    best_traveling_time = Field()      # 景点最佳旅游时间
    helpful_num = Field()              # 认为有用的人数
    scenicspot_name = Field()          # 景点名称
    scenicspot_intro = Field()         # 景点的简介
    scenicspot_address = Field()       # 景点的地址
    scenicspot_tel = Field()           # 景点的电话
    scenicspot_webaddress = Field()    # 景点的官网
    scenicspot_ticket = Field()        # 景点的票价
    scenicspot_opentime = Field()      # 景点开放时间
    scenicspot_usedtime = Field()      # 
    scenicspot_grade = Field()         # 景点的等级,如：3A,4A,5A...
    scenicspot_commentnum = Field()    # 对景点的评论数量

