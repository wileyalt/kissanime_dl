# -*- coding: utf-8 -*-

import js2py

def cVunicode(any):
    try:
        return unicode(any, utf8)
    except NameError:
        return str(any)


def convJStoPy(string):
    string = cVunicode(string)
    return js2py.eval_js(string)

def jsFuckDecode(string):
    removeeval = string[828:-3]
    return js2py.eval_js(removeeval)
