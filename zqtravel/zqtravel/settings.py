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
 'zqtravel.pipelines.TravelPipeline': 800,
 'zqtravel.pipelines.ScenicspotPipeline': 801,
}

#DOWNLOAD_HANDLERS = {
#    'http': 'zqtravel.scrapyjs.dhandler.WebkitDownloadHandler',
#    'https': 'zqtravel.scrapyjs.dhandler.WebkitDownloadHandler',
#}

#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36'

WEBKIT_DOWNLOADER=['mafengwo', 'ctrip']

#DOWNLOADER_MIDDLEWARES = {
    #'zqtravel.scrapyjs.middleware.WebkitDownloader': 1,
#     'zqtravel.downloader.WebkitDownloader': 3,
#}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zqtravel (+http://www.yourdomain.com)'
