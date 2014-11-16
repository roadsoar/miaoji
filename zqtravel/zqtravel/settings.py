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

LOG_FILE = '/home/fedr17/log/mj_travel.log'

ITEM_PIPELINES = {
 'zqtravel.pipelines.JsonWriterPipeline': 800,
}

#DOWNLOAD_HANDLERS = {
#    'http': 'MJTravel.scrapyjs.dhandler.WebkitDownloadHandler',
#    'https': 'MJTravel.scrapyjs.dhandler.WebkitDownloadHandler',
#}

#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36'

WEBKIT_DOWNLOADER=['mafengwo', 'ctrip']

#DOWNLOADER_MIDDLEWARES = {
    #'MJTravel.scrapyjs.middleware.WebkitDownloader': 1,
#     'zqtravel.downloader.WebkitDownloader': 3,
#}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zqtravel (+http://www.yourdomain.com)'
