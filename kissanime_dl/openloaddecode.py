# -*- coding: utf-8 -*-
# autor: vitas@matfyz.cz
# licence: public domain

# Edits done for kissanime-dl
# added cross version chr (cVchr)
# modified itoa

import re
import sys


def cVchr(txt):
    try:
        return unichr(txt)
    except NameError:
        return chr(txt)


def cVstr(txt):
    try:
        return unicode(txt)
    except NameError:
        return str(txt)

# no atoi in python, really?
# atoi stolen from: http://www.codecodex.com/wiki/Base_conversion
# We have to write our own function for outputting to string with
# arbitrary base


def itoa(num, radix):
    result = ""
    while num > 0:
        result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
        num /= radix
        num = int(num)
    return result


def openload_level2_debase(m):
    radix, num = int(m.group(1)) + 27, int(m.group(2))
    return '"' + itoa(num, radix) + '"'


def openload_level2(txt):
    return re.sub(r'\u01c3\((\d+),(\d+)\)', openload_level2_debase, txt, re.UNICODE).replace('"+"', '')


def openload_decode(txt):
    c = [

        ('_', '(ﾟДﾟ) [ﾟΘﾟ]'),
        ('a', '(ﾟДﾟ) [ﾟωﾟﾉ]'),
        ('b', '(ﾟДﾟ) [ﾟΘﾟﾉ]'),
        ('c', '(ﾟДﾟ) [\'c\']'),
        ('d', '(ﾟДﾟ) [ﾟｰﾟﾉ]'),
        ('e', '(ﾟДﾟ) [ﾟДﾟﾉ]'),
        ('f', '(ﾟДﾟ) [1]'),

        ('o', '(ﾟДﾟ) [\'o\']'),
        ('u', '(oﾟｰﾟo)'),
        ('c', '(ﾟДﾟ) [\'c\']'),

        ('9', '???'),
        ('8', '???'),

        ('7', '((ﾟｰﾟ) + (o^_^o))'),
        ('6', '((o^_^o) +(o^_^o) +(c^_^o))'),
        ('5', '((ﾟｰﾟ) + (ﾟΘﾟ))'),
        ('4', '(-~3)'),
        ('3', '(-~-~1)'),
        ('2', '(-~1)'),
        ('1', '(-~0)'),
        ('0', '((c^_^o)-(c^_^o))'),
    ]
    delim = "(ﾟДﾟ)[ﾟεﾟ]+"
    ret = ''
    for aachar in txt.split(delim):
        for i in range(len(c)):
            val, pat = c[i]
            aachar = aachar.replace(pat, val)
        aachar = aachar.replace('+ ', '')
        m = re.match(r'^\d+', aachar)
        if m:
            ret += cVchr(int(m.group(0), 8))
        else:
            m = re.match(r'^u([\da-f]+)', aachar)
            if m:
                # print "g:", m.group(1), int(m.group(1), 16)
                # this is hella hacky
                ret += cVchr(int(m.group(1), 16))
    # print "ret:", ret
    return openload_level2(ret)
