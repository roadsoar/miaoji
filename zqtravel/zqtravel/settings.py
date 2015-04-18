# -*- coding: utf-8 -*-

# Scrapy settings for zqtravel project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'zqtravel'

SPIDER_MODULES = ['zqtravel.spiders']
NEWSPIDER_MODULE = 'zqtravel.spiders'

LOG_FILE = '/home/scrapy/log/zqtravel.log'

ITEM_PIPELINES = {
 
 'zqtravel.pipelines.TravelPipeline': 802,
# 'zqtravel.pipelines.ScenicspotPipeline': 801,
# 'zqtravel.pipelines.ImagesStorePipeline': 1,
# 'zqtravel.pipelines.TravelLinkPipeline': 803
# 'scrapy.contrib.pipeline.images.ImagesPipeline': 1,
}

IMAGES_MIN_HEIGHT = 110
IMAGES_MIN_WIDTH = 110
IMAGES_EXPIRES = 90   # 90天的图片失效期限
IMAGES_STORE = '/home/scrapy/data/mafengwo_pic/'

#DOWNLOAD_HANDLERS = {
#    'http': 'zqtravel.scrapyjs.dhandler.WebkitDownloadHandler',
#    'https': 'zqtravel.scrapyjs.dhandler.WebkitDownloadHandler',
#}

#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36'

WEBKIT_DOWNLOADER=['mafengwo', 'mafengwo_scenicspot', 'mafengwo_province', 'ctrip', 'mafengwo_travel']

DOWNLOADER_MIDDLEWARES = {
#    'zqtravel.scrapyjs.middleware.WebkitDownloader': 1,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'zqtravel.middleware.rotate_useragent.RotateUserAgentMiddleware': 300,
#     'zqtravel.downloader.WebkitDownloader': 3,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zqtravel (+http://www.yourdomain.com)'

# 启用AutoThrottle扩展
AUTOTHROTTLE_ENABLED = True
# 是否启用cookies middleware。如果关闭，cookies将不会发送给web server。
COOKIES_ENABLED = True
# 单位是妙。下载器在下载同一个网站下一个页面前需要等待的时间。该选项可以用来限制爬取速度， 减轻服务器压力。同时也支持小数
DOWNLOAD_DELAY = 1

# 让爬取的质量更高，使用宽度优先的策略
#SCHEDULER_ORDER = 'BFO'

# 启用调试
DUPEFILTER_DEBUG = True
