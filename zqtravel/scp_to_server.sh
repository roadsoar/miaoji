#!/bin/bash

SOURCE='/home/chunchen/Music/miaoji/zqtravel'
#SOURCE='/home/chunchen/Music/.miaoji/back/zqtravel'
#DATA_SOURCE='/home/scrapy/data/mafengwo.bak20150319'
DESTINATION='~/travel'

scp -r -p -P12301 $SOURCE $DATA_SOURCE root@121.41.20.59:$DESTINATION