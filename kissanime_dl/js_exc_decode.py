# -*- coding: utf-8 -*-

import re

def cVstr(txt):
	try:
		return unicode(txt)
	except NameError:
		return str(txt)

def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
	return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

def exclaFunc(string):
	split_str = string.split(',')
	split_str[1] = split_str[1].replace(" ", '')
	return baseN(int(split_str[1]), int(split_str[0]) + 27)

def jsdecode(raw_str):
	raw_str = raw_str.encode('utf8')
	regex = re.compile(r'ǃ\((?:.*?)\)', re.UNICODE)
	parsed = regex.findall(raw_str)

	for sing_val in parsed:
		raw_str = raw_str.replace(sing_val, '"' + exclaFunc(sing_val.replace("ǃ(", "").replace(")", "") ) + '"')

	str_split = raw_str.replace(" ", '').split("+")

	fin_data = ''
	for val in str_split:
		val = val.replace("\"", "")
		val = val.replace("\'", "")

		fin_data = fin_data + val
	return fin_data