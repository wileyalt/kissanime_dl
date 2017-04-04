# -*- coding: utf-8 -*-
# By WILEY YU

import time
import re
import threading
import sys
try:
    # python2
    from urllib import unquote
except ImportError:
    # python3
    from urllib.parse import unquote

import requests
from lxml import html

try:
    from kissenc import kissencCartoon, kissencAsian, kissencAnime
except ImportError:
    from .kissenc import kissencCartoon, kissencAsian, kissencAnime
try:
    from color_print import Color, printClr
except ImportError:
    from .color_print import Color, printClr
try:
    from js_exc_decode import jsdecode2
except ImportError:
    from .js_exc_decode import jsdecode2

mu = threading.Lock()
print_mu = threading.Lock()

DOWNLOAD_URL_X_PATH = "//select[@id='slcQualix']"
DOWNLOAD_URL_X_PATH_DEFAULT = DOWNLOAD_URL_X_PATH + "/option[1]/@value"
DOWNLOAD_FILENAME = "//div[@id='divFileName']/b/following::node()"

# arr of all the escape chars
escapes = ''.join([chr(char) for char in range(1, 32)])

# NAME = 0
# DOWNLOAD_URL = 1
# PARENT_URL = 2

# cross version
def uprint(any):
    try:
        any.encode(sys.stdout.encoding)
        if isinstance(any, str) and sys.version_info < (3, 0, 0):
            print(any.encode('utf-8').strip() )
            return
        print(any)
    except UnicodeEncodeError:
        return "Unsupported characters in " + sys.stdout.encoding

class ERROR_RETURN:
    NO_ERROR = 0
    NO_FILENAME = 1
    DECODE_FAIL = 2

def getBlogspotUrls(link, ses, sleeptime, quality_txt, verbose=False):
    genned_x_path = DOWNLOAD_URL_X_PATH
    error_type = ERROR_RETURN.NO_ERROR

    if(quality_txt != ""):
        genned_x_path = genned_x_path + \
            "/option[normalize-space(text() ) = \'" + \
            quality_txt + "\']/@value"
    else:
        # defaults to highest quality
        genned_x_path = DOWNLOAD_URL_X_PATH_DEFAULT

    time.sleep(sleeptime)

    # lets make a copy
    dl_url_x_path = genned_x_path

    payload = {"s": "kissanime"}

    mu.acquire()
    html_raw = ses.get(link, params=payload)
    mu.release()

    html_str = html_raw.content

    temp_tree = html.fromstring(html_str)
    raw_data = temp_tree.xpath(DOWNLOAD_FILENAME)

    discovered_url = ""

    if("/Anime/" in link):
        # site is kissanime
        discovered_url = kissencAnime(temp_tree.xpath(dl_url_x_path)[0], ses)
    elif("/Cartoon/" in link):
        # site is kisscartoon
        discovered_url = kissencCartoon(
            temp_tree.xpath(dl_url_x_path)[0], ses)
    elif("/Drama/" in link):
        # site is kissasian
        discovered_url = kissencAsian(
            temp_tree.xpath(dl_url_x_path)[0], ses)
    else:
        # unknown site
        printClr("Error in finding method to decode video url from " +
                 link, Color.RED, Color.BOLD)
        return [ERROR_RETURN.DECODE_FAIL]

    format_txt = ""

    if(len(raw_data) == 0):
        printClr("Error in finding filename.", Color.BOLD, Color.RED)
        format_txt = link
        error_type = ERROR_RETURN.NO_FILENAME
    else:
        def findName():
            def sanitize(funky_str):
                # removes all those escape chars from the string
                try:
                    ft = funky_str.replace(" ", '').translate(None, escapes)
                except TypeError:
                    try:
                        ft = funky_str.replace(" ", '').translate(
                            str.maketrans(dict.fromkeys(escapes)))
                    except AttributeError:
                        # python 2
                        ft = funky_str.replace(" ", '').translate(
                            dict.fromkeys(escapes))

                return ft

            format_txt = sanitize(raw_data[0])

            # With email protection, sometimes only the [ is shown
            if(format_txt == "["):
                # hmm. this is a hacky fix
                # The rest of the data is generally in 5?
                format_txt = format_txt + sanitize(raw_data[5])

                # no quality found
            if(len(temp_tree.xpath(dl_url_x_path)) == 0 and quality_txt != ""):
                printClr("Quality " + quality_txt +
                         " is not found", Color.RED, Color.BOLD)
                printClr("Defaulting to highest quality", Color.BOLD)
                dl_url_x_path = DOWNLOAD_URL_X_PATH_DEFAULT

        findName()

    if(verbose):
        print_mu.acquire()
        uprint("Found download link: " + discovered_url)
        uprint("Found file name: " + format_txt)
        print_mu.release()

    return [error_type, format_txt, discovered_url, link]