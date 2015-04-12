#!/bin/bash

function delete_duplicate_file()
{
root_dir='/home/scrapy/data/mafengwo_scenicspot'
bak_dir='/home/scrapy/data/mafengwo_scenicspot.bak'
# mafengwo_province.bak

cat /dev/null > ./test.txt
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
# 遍历省
for province in `ls $root_dir`
do
  province_path=${root_dir}/$province
  if [ -d $province_path ]
  then
    # 遍历市/县
    for city in `ls $province_path`
    do
      city_path=$province_path/$city
      if [ -d $city_path ]
      then
        # 遍历景点
        for scenicspot in `ls $city_path`
        do
          scenicspot_path=$city_path/$scenicspot
          files=`ls "${scenicspot_path}"`
          file_num=`ls "${scenicspot_path}" | wc -l`
          if [ $file_num -gt 1 ]
          then
            #echo $files | sort >> ./test.txt
            echo $scenicspot_path | sort >> ./test.txt
            file=`echo $files | sort |awk '{print $1}'`
            bak_scenicspot_path="$bak_dir/$province/$city/$scenicspot"
            if [ ! -d $bak_scenicspot_path ]
            then
              mkdir -p $bak_scenicspot_path
            fi
            mv $scenicspot_path/$file $bak_scenicspot_path
          fi
        done
      fi
    done
  fi
done
IFS=$SAVEIFS
}

function delete_duplicate_line()
{
  file_dir_root='/home/scrapy/data/travel_urls' 
  bak_dir="${file_dir_root}.origin_all"
  # 备份原始数据
  if [ ! -d $bak_dir ]
  then
      mkdir -p $bak_dir
  fi
  cp -r $file_dir_root/* $bak_dir
  # 删除文件中重复的行
  for province in `ls $file_dir_root`
  do
    province_path=$file_dir_root/$province
    for file in `ls $province_path`
    do
      file_name=$province_path/$file
      sort -u $file_name -o $file_name
    done
  done
}

case $1 in
line) delete_duplicate_line;;
file) delete_duplicate_file;;
*)     echo 'Only accept "line" or "file"';;
esac
