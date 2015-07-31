#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import re
import time
import hashlib
from math import *

#double check����Ŀ¼, ��exit_if_failure ȡֵΪTrueʱ������ʧ���˳�
def makeDirsWithDoubleCheck(dir_name, exit_if_failure=True):
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError:
            if not os.path.exists(dir_name):
                if exit_if_failure:
                    sys.exit(1)

#У���ַ���Ϊ����ֵ����exit_if_failure ȡֵΪTrueʱ�������˳�
def checkDigitValid(str_value, exit_if_failure=True):
    if not str_value.isdigit():
        if exit_if_failure:
            print "%s is not a digit" % str_value
            sys.exit(1)
        return False
    return True

#У���ƶ��ļ��Ƿ���ڣ���exit_if_failure ȡֵΪTrueʱ�������˳�
def checkFileValid(file_name, exit_if_failure=True):
    if not os.path.isfile(file_name):
        if exit_if_failure:
            print "%s is not a valid file" % file_name
            sys.exit(1)
        return False
    return True

#У���ƶ��ļ����Ƿ���ڣ���exit_if_failure ȡֵΪTrueʱ�������˳�
def checkDirValid(dir_name, exit_if_failure=True):
    if not os.path.isdir(dir_name):
        if exit_if_failure:
            print "%s is not a valid dir" % dir_name
            sys.exit(1)
        return False
    return True

#�����ļ���һ��map��, num_key_fields ָ�����key��field������num_value_fieldsָ��value��field������delimiterָ���ָ���
#map_key_list��keyΪ�ַ�����valueΪlist
def loadFileIntoMap(file_name, num_key_fields, num_value_fields, map_key_list, delimiter="|"):
    if checkFileValid(file_name,False) == False:
        return
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if num_key_fields + num_value_fields > len(items):
            continue
        map_key_list[delimiter.join(items[0:num_key_fields])] = items[num_key_fields:(num_key_fields + num_value_fields)]

#�����ļ���һ��map��, list_keys ָ�����е�key index��num_fieldsָ��value��field������delimiterָ���ָ���
#map_key_list��keyΪ�ַ�����valueΪlist
def loadFileKeysValuesIntoMap(file_name, list_keys, num_fields, map_key_list, delimiter="|"):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if num_fields > len(items):
            continue
        key = ""
        for key_index in list_keys:
            key += items[key_index] + delimiter
        map_key_list[key] = items[0:num_fields]

#�����ļ���һ��map��, num_key_fields ָ�����key��field����,  num_fieldsָ��field��������delimiterָ���ָ���
#map_key_list��keyΪ�ַ�����valueΪlist
def loadFileFieldsIntoMap(file_name, num_key_fields, num_fields, map_key_list, delimiter="|"):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if num_fields > len(items):
            continue
        map_key_list[delimiter.join(items[0:num_key_fields])] = items[0:num_fields]

#����key, value��ʽ���ļ���map��
def loadFileKeyValue(file_name, map_key_value, delimiter="|", duplicate_prompt=False):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if 2 > len(items):
            continue
        if duplicate_prompt:
            if items[0] in map_key_value and map_key_value[items[0]] != items[1]:
                print "duplicate in file:%s, key:%s, old value:%s, new value:%s" % \
                        (file_name, items[0], map_key_value[items[0]], items[1])
        map_key_value[items[0]] = items[1]

#����key, value��ʽ���ļ���map��
def loadFileIntKeyValue(file_name, map_key_value, group_num, group_index, delimiter="|", duplicate_prompt=False):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if 2 > len(items):
            continue
        if not items[0].isdigit() or not items[1].isdigit():
            continue
        key = int(items[0])
        if group_index != key % group_num:
            continue
        value = int(items[1])
        if duplicate_prompt:
            if key in map_key_value and map_key_value[key] != value:
                print "duplicate in file:%s, key:%s, old value:%s, new value:%s" % \
                        (file_name, key, map_key_value[key], value)
        map_key_value[key] = value

#�����ļ���set��
def loadFileIntoSet(file_name, set_values):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        set_values.add(line)

#�����ļ���ָ���е�set��
def loadFileFieldsIntoSet(file_name, num_key_fields, set_values, delimiter="|"):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if num_key_fields > len(items):
            continue
        set_values.add(delimiter.join(items[0:num_key_fields]))

#�����ļ���list��
def loadFileIntoList(file_name, data_list, delimiter='|'):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        #items = line.split(delimiter)
        data_list.append(line)

#�����ļ���list��, list�е�valueΪstring����
def loadFileFieldsIntoList(file_name, num_fields, data_list, delimiter='|', if_join=True):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if num_fields > len(items):
            continue
        if if_join:
            data_list.append(delimiter.join(items[0:num_fields]))
        else:
            data_list.append(items[0:num_fields])

#�ж��ַ����Ƿ�Ϊ������
def isFloat(str_value):
    try:
        float(str_value)
        return True
    except ValueError:
        return False

#�����ļ���һ��map�У��ļ���ʽΪvalue|key1|key2|key3
#map_key_list���� key1 -> value, key2 -> value
def loadWordsMap(file_name, map_key_value, delimiter="|"):
    for line in file(file_name):
        line = line.strip()
        if not line:
            continue
        items = line.split(delimiter)
        if 2 > len(items):
            continue
        for i in range(1, len(items)):
            map_key_value[items[i]] = items[0]

#��ȡ��ǰ����ռ���ڴ���
def getMemUsage():
    pid = os.getpid()
    filename = "/proc/%d/status" % pid
    if not os.path.exists(filename):
        print 'can not open pid file'
        return -1
    for line in file(filename):
        line = line.strip()
        if not line:
            continue
        if -1 < line.find("VmRSS:"):
            r_list = re.findall('(\d+)', line)
            if len(r_list) > 0:
                m_byte = int(r_list[0]) / 1024 # KB => MB
                return m_byte
    return -1

#��ȡ�û���Դ
def getMsisdnLocation(imsi, msisdn, base_province, base_city, imsi_mccmnc, msisdn_hlr, location_value=["", ""]):
    province = ""
    city = ""
    location = 3
    mccmnc = imsi_mccmnc.queryMccMncbyImsi(imsi)
    if None != mccmnc:
        country = mccmnc.country
        if "�й�" != country:
            location = 4
        if msisdn:
            hlr = msisdn_hlr.queryHlrByEncryptMsisdn(msisdn)
            if None != hlr:
                province = hlr.province
                city = hlr.city
                if base_city == city:
                    location = 1
                elif base_province == province:
                    location = 2
    if not province:
        province = "����"
    if not city:
        city = "����"
    location_value[0] = province
    location_value[1] = city
    return location

def getTimeByMinute(time_minute):
    return time.mktime(time.strptime(time_minute, "%Y%m%d%H%M"))

def getTimeBySecond(time_second):
    return time.mktime(time.strptime(time_second, "%Y%m%d%H%M%S"))

def getMinuteByTime(time_seconds):
    local_time = time.localtime(time_seconds)
    time_minute = "%.4d%.2d%.2d%.2d%.2d" % (local_time.tm_year, local_time.tm_mon, local_time.tm_mday, local_time.tm_hour, local_time.tm_min)
    return time_minute

def md5(str):
    m = hashlib.md5() 
    m.update(str)
    return m.hexdigest()

# input Lat_A γ��A
# input Lng_A ����A
# input Lat_B γ��B
# input Lng_B ����B
# output distance ����(km)
def calcDistance(Lat_A, Lng_A, Lat_B, Lng_B):
    ra = 6378.140  # ����뾶 (km)
    rb = 6356.755  # ���뾶 (km)
    flatten = (ra - rb) / ra  # �������
    rad_lat_A = radians(Lat_A)
    rad_lng_A = radians(Lng_A)
    rad_lat_B = radians(Lat_B)
    rad_lng_B = radians(Lng_B)
    pA = atan(rb / ra * tan(rad_lat_A))
    pB = atan(rb / ra * tan(rad_lat_B))
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (xx + dr)
    return distance

