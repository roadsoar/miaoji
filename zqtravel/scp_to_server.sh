#!/bin/bash

SOURCE='/home/chunchen/Music/miaoji/zqtravel'
ScpFile='load_to_db.py'
shellFile='delete_duplicate_scenicspots.sh'
sqlFile='*.sql'
#DATA_SOURCE='/home/scrapy/data/mafengwo_scenicspot'
#DATA_SOURCE='/home/scrapy/data_201220/mafengwo'
DESTINATION='~'
USER='chency'
PASSWd='(!@#QWE,,..)'

scp -r -p -P22 $SOURCE $DATA_SOURCE $USER@202.85.216.77:$DESTINATION
#scp -r -p -P22 $SOURCE/$ScpFile $SOURCE/$shellFile $SOURCE/$sqlFile $USER@202.85.216.77:$DESTINATION



## 为tar加密/解密
## 加密压缩
#  tar czf - ${待压缩的目录或文件} | openssl des3 -salt -k ${明文密码}| dd of=${压缩后的文件名}
## 解密解压
#  dd if=${压缩文件} | openssl des3 -d | tar xzf -
