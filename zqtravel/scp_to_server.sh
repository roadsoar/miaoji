#!/bin/bash

SOURCE='/home/chunchen/Music/miaoji/zqtravel'
SOURCE_IMAGE='/home/scrapy/data/mafengwo_images'
SOURCE_TRAVEL='/home/scrapy/data/mafengwo_travel'
#SOURCE_SCENICSPOT='/home/scrapy/data/mafengwo_scenicspot'
ScpFile='load_to_db.py'
shellFile='delete_duplicate_scenicspots.sh'
sqlFile='*.sql'
DESTINATION='~'
DESTINATION_IMAGE='/home/images'
USER='chency'
PASSWd='(!@#QWE,,..)'

scp -r -p -P22 $SOURCE $SOURCE_SCENICSPOT $USER@202.85.216.77:$DESTINATION
#scp -r -p -P22 $SOURCE_TRAVEL $SOURCE_IMAGE $USER@202.85.216.77:$DESTINATION_IMAGE



## 为tar加密/解密
## 加密压缩
#  tar czf - ${待压缩的目录或文件} | openssl des3 -salt -k ${明文密码}| dd of=${压缩后的文件名}
## 解密解压
#  dd if=${压缩文件} | openssl des3 -d | tar xzf -
