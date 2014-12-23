#!/bin/bash

cd /home/chunchen/Music/.miaoji/back/zqtravel/zqtravel


date >> ./done.txt

for province in `cat ./province.txt`
do
try_times=0
while [ $try_times -le 3 ]
do
ps -ef |grep scrapy |grep -v grep
res=$(echo $?)
if [ $res -ne 0 ]
then
   sedstr="sed -i '/mafengwo_spider/,/^start_urls/s/[0-9]\+/$province/' ./spider_settings.cfg"
   eval $sedstr
   scrapy crawl mafengwo &
   echo $province>>./done.txt
   break
else
   sleep_sec=`echo "(2-0.5*$try_times)*60*60"|bc`
   sleep $sleep_sec
fi
done
done
