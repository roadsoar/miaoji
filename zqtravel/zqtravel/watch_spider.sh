#!/bin/bash

# ******
# 这是一个监控爬虫进程的脚本
# 当爬虫爬取期间，遇到异常，需要及时停止爬虫，以确保接续爬取
#
# cd $spider_start_home
# 爬虫启动命令行, 须设置JOBDIR来支持接续爬取
# nohup scrapy crawl mafengwo -s JOBDIR=/home/scrapy/data/m1412231 &
# ******

spider_start_home=/home/chunchen/Music/.miaoji/back/zqtravel/zqtravel
spider_log='/home/scrapy/log/zqtravel.log'
err_threshold=6
warn_threshold=3
SLEEP_TIME=60 #单位：秒

spider_mafengwo_pid=$(ps -ef |grep scrapy |grep mafengwo |grep -v grep |awk '{print $2}')

while [ "True" ]
do
warn1_count=$(grep -i "Filtered offsite request" $spider_log | wc -l)
err_500_count=$(grep -i "Internal Server Error" $spider_log | wc -l)
err2_count=$(grep -i "ERROR" $spider_log | wc -l)

if [ ${err_500_count} -ge $err_threshold -o $err2_count -ge $err_threshold -o $warn1_count -ge $warn_threshold ];
then
  #只能发送SIGINT信号一次，然后等着spider进程自己结束，否则达不到增量爬取网页的目的
  kill -2 $spider_mafengwo_pid
  sleep $SLEEP_TIME  # 等带进程结束
  echo "<`date`> 请更换IP（eg: 重启路由），再启动爬虫程序！" > $spider_log
  echo -e "错误统计:\nFiltered offsite request: $warn1_count次, Internal Server Error: ${err_500_count}次, ERROR: $err2_count次">>$spider_log

  # 如果不是被网站封禁，则重启爬虫
  if [ ${err_500_count} -lt $err_threshold ];
  then
    sleep $SLEEP_TIME
    ps -ef |grep scrapy |grep mafengwo |grep -v grep
    res=`echo $?`
    if [ $res -ne 0 ];
    then
      cd $spider_start_home
      nohup scrapy crawl mafengwo -s JOBDIR=/home/scrapy/data/m1412231 &
    fi
  else
    break
  fi

fi

sleep $SLEEP_TIME
done

