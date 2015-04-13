#!/bin/bash

SOURCE='/home/chunchen/Music/miaoji/zqtravel'
DATA_SOURCE='/home/scrapy/data/mafengwo_scenicspot'
DESTINATION='~/travel'
USER='root'

scp -r -p -P12301 $SOURCE $DATA_SOURCE $USER@121.41.20.59:$DESTINATION



## 为tar加密/解密
## 加密压缩
#  tar czf - ${待压缩的目录或文件} | openssl des3 -salt -k ${明文密码}| dd of=${压缩后的文件名}
## 解密解压
#  dd if=${压缩文件} | openssl des3 -d | tar xzf -
