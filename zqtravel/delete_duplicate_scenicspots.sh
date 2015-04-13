#!/bin/bash

function delete_duplicate_file()
{
# 全部的景点信息
root_dir='/home/scrapy/data/mafengwo_scenicspot'
bak_dir='/home/scrapy/data/mafengwo_scenicspot.moved'
# 不全的景点信息
#root_dir='/home/scrapy/data/mafengwo_province'
#bak_dir='/home/scrapy/data/mafengwo_province.moved'

echo "************The handled scenispots as below***********" > ./rs.txt
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
            echo $scenicspot_path | sort >> ./rs.txt
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

# 删除目录下文件中的重复行
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

function get_scenispot_num()
{
  root_dir='/home/scrapy/data/mafengwo_scenicspot'
  for province in `ls $root_dir`
  do
    province_path="$root_dir/$province"
    each_city_num=`ls $province_path |wc -l`
    echo "$each_city_num" >> .tmpccy
  done
  all_num=`find $root_dir -type f | wc -l`
  province_num=`ls $root_dir |wc -l`
  province_and_city_num=`awk '{sum+=$1}END{print sum}' .tmpccy`
  let city_num=$province_and_city_num-$province_num
  let scenicspot_num=$all_num-$province_and_city_num
  echo "Province Num: $province_num"
  echo "City Num: $city_num"
  echo "Scenicspot Num: $scenicspot_num"
  rm .tmpccy
}

function main()
{
case $1 in
line) delete_duplicate_line;;
file) delete_duplicate_file;;
num) get_scenispot_num;;
*)     echo 'Only accept "line" or "file"';;
esac
}

main $1
