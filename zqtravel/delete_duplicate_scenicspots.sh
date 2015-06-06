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

function do_merge()
{
  if [ -f $1 ]
  then
     num=`wc -l $1|awk '{print $1}'`
     if [ $num -gt 1 ]
     then
       cat $1 |tr -d '\n' > tmp.txt
       cat tmp.txt > $1 && rm tmp.txt
     fi
  fi
}


function merge_lines()
{
# 景点信息
root_dir='/home/scrapy/data/mafengwo_scenicspot'
#root_dir='/root/travel/mafengwo_data'

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
# 遍历省
for province in `ls $root_dir`
do
  province_path=${root_dir}/$province
  do_merge $province_path
  if [ -d $province_path ]
  then
    # 遍历市/县
    for city in `ls $province_path`
    do
      city_path=$province_path/$city
      do_merge $city_path
      if [ -d $city_path ]
      then
        # 遍历景点
        for scenicspot in `ls $city_path`
        do
          scenicspot_path=$city_path/$scenicspot
          files=`ls "${scenicspot_path}"`
          file_num=`ls "${scenicspot_path}" | wc -l`
          if [ $file_num -eq 1 ]
          then
             do_merge $scenicspot_path/$files
          else
            echo "$scenicspot_path" >> need_do.txt
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

function remove_specific_string()
{
  file_dir_root='/home/scrapy/data/travel_urls'
  # 删除文件中小括号及其之间的内容，如：(Secem info)
  for province in `ls $file_dir_root`
  do
    province_path=$file_dir_root/$province
    for file in `ls $province_path`
    do
      file_name=$province_path/$file
      sed -i -e 's#\(.*\)\(（.*|\)\(.*\)#\1|\3#g' -e 's#\(.*\)\((.*|\)\(.*\)#\1|\3#g' $file_name
      #sed -i -e 's#\(.*\)\(（.*）\)\(.*\)#\1\3#g' -e 's#\(.*\)\((.*)\)\(.*\)#\1\3#g' -e 's#\(.*\)\((.*）\)\(.*\)#\1\3#g' -e 's#\(.*\)\(（.*)\)\(.*\)#\1\3#g' $file_name
    done
  done
}

function main()
{
case $1 in
line ) delete_duplicate_line;;
file ) delete_duplicate_file;;
num  ) get_scenispot_num;;
merge) merge_lines;;
spec ) remove_specific_string;;
    *) echo 'Only accept "line", "file", "num", "merge", "spec"'
       echo '"line": 删除文件中重复的行'
       echo '"file": 删除景点目录中重复的文件'
       echo '"num" : 计算景点的个数'
       echo '"merge": 将景点文件将多行合并成一行'
       echo '"spec": 删除文件中小括号及其之间的内容，如：(Secem info)'
       ;;
esac
}

main $1
