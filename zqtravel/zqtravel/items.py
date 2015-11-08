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

class TravelItem(Item):
    '''蚂蜂窝的游记条目'''

    travel_praisenum = Field()        # 游记被赞的数量
    travel_viewnum = Field()          # 游记的浏览数量
    travel_commentnum = Field()       # 游记的评论数量
    travel_comments = Field()         # 游记的评论
    travel_title = Field()            # 游记的标题
    travel_create_time = Field()      # 游记文章创建的时间
    travel_time = Field()             # 游玩的时间
    travel_people = Field()           # 游玩的人数
    travel_cost = Field()             # 游玩的费用
    travel_type = Field()             # 游玩的形式
    travel_days = Field()             # 游玩的天数
    travel_link = Field()             # 游记的链接
    scenicspot_in_trip = Field()      # 游记中涉及的景点，针对蝉游记
    scenicspot_in_trip = Field()      # 游记中涉及的景点，针对蝉游记
    from_url = Field()                # 游记link是从from_url跳转过来的
    travel_content = Field()          # 游记的内容
    scenicspot_province = Field()     # 景点所在地，即所在的省
    scenicspot_name = Field()         # 景点名称
    scenicspot_locus = Field()        # 景点所在地，即所在的省/市/县
                                      # scenicspot_name和scenicspot_locus，是为了区分游记文件的路径
    trip_roadmap = Field()            # 游记路线
    roadmap_detail = Field()          # 详细的游记路线
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
    from_url = Field()                 # 景点link是从from_url跳转过来的
    area = Field()                     # 
    abstract = Field()                 # 省市概况
    num_days = Field()                 # 建议游玩天数
    weather = Field()                  # 穿衣指南
    language = Field()                 # 地方语言特色简介
    best_traveling_time = Field()      # 景点最佳旅游时间
    helpful_num = Field()              # 认为有用的人数
    traffic = Field()                  # 交通
    history = Field()                  # 历史
    custom = Field()                   # 风俗禁忌
    culture = Field()                  # 宗教与文化
    scenicspot_name = Field()          # 景点名称
    scenicspot_intro = Field()         # 景点的简介
    scenicspot_address = Field()       # 景点的地址
    scenicspot_tel = Field()           # 景点的电话
    scenicspot_webaddress = Field()    # 景点的官网
    scenicspot_ticket = Field()        # 景点的票价
    scenicspot_opentime = Field()      # 景点开放时间
    scenicspot_usedtime = Field()      # 景点游玩时间参考
    scenicspot_grade = Field()         # 景点的等级,如：3A,4A,5A...
    scenicspot_commentnum = Field()    # 对景点的评论数量
    scenicspot_impression = Field()    # 对景点的印象
    scenicspot_comments = Field()      # 对景点的前6条评论
    scenicspot_dressing = Field()      # 去景点时的穿衣建议

class POIItem(Item):
    '''信息点条目,如餐馆·旅店'''

    province = Field()
    city = Field()
    from_url = Field()
    poi_name = Field()             # 名称
    poi_star = Field()            # poi的星级
    poi_commentnum = Field()      # 对poi的评论数
    poi_cost = Field()            # 在poi的消费
    poi_catalog = Field()         # poi的类别
    poi_addr = Field()            # poi的地址
    poi_kouwei = Field()          # 口味
    poi_huanjing = Field()        # poi的环境
    poi_service = Field()         # poi的服务水平
    poi_pic = Field()             # poi的图片
    poi_link = Field()            # poi的链接
