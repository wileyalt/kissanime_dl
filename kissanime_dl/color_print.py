# -*- coding: utf-8 -*-
# By Wiley Yu

# unicode colors!


class Color:
    BEG = '\033['
    SEP = ';'
    BOLD = '1'
    RED = '31'
    GREEN = '32'
    YELLOW = '33'
    END_BEG = 'm'
    END = '\033[0m'


def printClr(string, *args):
    # we have to work backwards
    string = Color.END_BEG + string

    fst = False
    for arg in args:
        if(fst is False):
            string = arg + string
            fst = True
            continue

        string = Color.SEP + string
        string = arg + string

    string = Color.BEG + string
    print(string + Color.END)
