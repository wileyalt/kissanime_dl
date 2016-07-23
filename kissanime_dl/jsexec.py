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
