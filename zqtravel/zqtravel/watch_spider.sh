#!/bin/bash

# ******
# 这是一个监控爬虫进程的脚本
# 当爬虫爬取期间，遇到异常，需要及时停止爬虫，以确保接续爬取
#
# cd $spider_start_home
# 爬虫启动命令行, 须设置JOBDIR来支持接续爬取
# nohup scrapy crawl $spider_name -s JOBDIR=$spider_job_dir_home/$job_dir_name &
# ******

##
## 为了使用方便，不建议强制退出脚本（即不使用 kill -9），本脚本没有对SIGKILL信号的处理
##
spider_name='mafengwo_scenicspot'
spider_start_home=$(pwd)
spider_job_dir_home='/home/scrapy/data'
spider_log='/home/scrapy/log/zqtravel.log'
err_threshold=8
warn_threshold=3
critical_threshold=1
SLEEP_TIME=2 #单位：秒

# 只允许一个watch_spider进程存在
#watch_processes=$(ps -ef |grep watch_spider |grep -v grep|wc -l)
#if [ $watch_processes -gt 1 ];
#then
#  echo -e "\033[32;49;1mWatch_spider is running...\033[39;49;0m"
#  exit 1
#fi

# 必须指定JOBDIR
if [ $# -ne 1 ];
then
  echo -e "\033[31;49;1m^^Need spider job directory name^^\033[39;49;0m"
  echo "Usage: $0 <spider_job_dir_name>"
  echo -e "\n\033[32;49;1mcheck the dir at: $spider_job_dir_home/<spider_job_dir_name>\033[39;49;0m"
  exit 1
fi

job_dir_name=$1

cat /dev/null > $spider_log
cd $spider_start_home
nohup scrapy crawl $spider_name -s JOBDIR=$spider_job_dir_home/$job_dir_name &

_exit()
{
  spider_mafengwo_pid=$(ps -ef |grep scrapy |grep $spider_name |grep -v grep |awk '{print $2}')
  kill -15 $spider_mafengwo_pid
  exit 0
}

trap '_exit' TERM INT

killed_spider=1
while [ "True" ]
do
warn1_count=$(grep -i "Filtered offsite request" $spider_log | wc -l)
err_500_count=$(grep -i -e "connection timed out" -e "not handled or not allowed" -e "Internal Server Error" -e "DNS lookup failed" -e "An error occurred while connecting" $spider_log | wc -l)
err2_count=$(grep -i -e "ERROR" -e "Errno" $spider_log | wc -l)
critical_error=$(grep -i -e "Unhandled Error" $spider_log | wc -l)

spider_mafengwo_pid=$(ps -ef |grep scrapy |grep $spider_name |grep -v grep |awk '{print $2}')

if [ ${err_500_count} -ge 1 -o $err2_count -ge $err_threshold -o $warn1_count -ge $warn_threshold -o $critical_error -ge $critical_threshold ];
then
  #只能发送SIGTERM/SIGINT信号一次，然后等着spider进程自己结束
  if [ $killed_spider -ne 0 ];
  then
    kill -15 $spider_mafengwo_pid
    killed_spider=0
    sleep $SLEEP_TIME  # 等带进程结束
    echo "<`date`> 请更换IP（eg: 重启路由），再启动爬虫程序！" > $spider_log
    echo -e "错误统计:\nFiltered offsite request: $warn1_count次, Internal Server Error: ${err_500_count}次, ERROR: $err2_count次">>$spider_log
  fi
fi

# 如果不是被网站封禁，则重启爬虫
if [ ${err_500_count} -lt 2 -a $critical_error -lt $critical_threshold ];
then
  ps -ef |grep scrapy |grep $spider_name |grep -v grep > /dev/null
  res=`echo $?`
  if [ $res -ne 0 ];
  then
    cd $spider_start_home
    nohup scrapy crawl $spider_name -s JOBDIR=$spider_job_dir_home/$job_dir_name &
    killed_spider=1
  fi
  sleep $SLEEP_TIME
else
  break
fi

sleep $SLEEP_TIME
done

