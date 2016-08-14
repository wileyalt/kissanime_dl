# -*- coding: utf-8 -*-

# decodes the function that looks like !(a, b)

# Wiley Yu

import re


def baseN(num, radix):
    result = ""
    while num > 0:
        result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
        num /= radix
        num = int(num)
    return result


def exclaFunc(string):
    try:
        split_str = string.split(',')
        split_str[1] = split_str[1].replace(" ", '')
        return baseN(int(split_str[1]), int(split_str[0]) + 27)
    except TypeError:
        split_str = string.split(b',')
        split_str[1] = split_str[1].replace(b" ", b'')
        return baseN(int(split_str[1]), int(split_str[0]) + 27)


def jsdecode(raw_str):
    raw_str = raw_str.encode('utf8')
    try:
        parsed = re.findall(r'ǃ\((?:.*?)\)', raw_str)
    except TypeError:
        parsed = re.findall('ǃ\((?:.*?)\)'.encode('utf8'), raw_str)

    try:
        for sing_val in parsed:
            raw_str = raw_str.replace(
                sing_val, '"' + exclaFunc(sing_val.replace("ǃ(", "").replace(")", "")) + '"')
    except TypeError:
        for sing_val in parsed:
            tempval = b'"' + \
                exclaFunc(sing_val.replace(
                    "ǃ(".encode('utf8'), b"").replace(b")", b"")).encode('utf8')
            raw_str = raw_str.replace(sing_val, tempval)

    try:
        str_split = raw_str.replace(" ", '').split("+")
    except TypeError:
        str_split = raw_str.replace(b" ", b'').split(b"+")

    fin_data = ''
    try:
        for val in str_split:
            val = val.replace("\"", "")
            val = val.replace("\'", "")
            fin_data = fin_data + val
    except TypeError:
        for val in str_split:
            val = val.replace(b'"', b"")
            val = val.replace(b"'", b"")
            fin_data = fin_data + val.decode('utf8')

    return fin_data

def jsdecode2(hiddenurl):
    data_str = ''
    for i in range(len(hiddenurl) - 1):
        #charcode@
        j = ord((hiddenurl[i]))
        if(j >= 33 and j <= 126):
            data_str = data_str + chr(33+((j+14)%94))
        else:
            data_str = data_str + chr(j)

    return data_str



