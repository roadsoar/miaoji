# -*- coding: utf-8 -*-

# Scrapy settings for MJTravel project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'MJTravel'

SPIDER_MODULES = ['MJTravel.spiders']
NEWSPIDER_MODULE = 'MJTravel.spiders'

ITEM_PIPELINES = {
 'MJTravel.pipelines.JsonWriterPipeline': 800,
}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'MJTravel (+http://you.crtip.com)'

#DOWNLOAD_HANDLERS = {
#    'http': 'MJTravel.scrapyjs.dhandler.WebkitDownloadHandler',
#    'https': 'MJTravel.scrapyjs.dhandler.WebkitDownloadHandler',
#}

#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36'

WEBKIT_DOWNLOADER=['MJCtrip']

DOWNLOADER_MIDDLEWARES = {
    #'MJTravel.scrapyjs.middleware.WebkitDownloader': 1,
     'MJTravel.downloader.WebkitDownloader': 3,
}
