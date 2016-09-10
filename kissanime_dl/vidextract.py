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

DOWNLOAD_URL_X_PATH = "//select[@id='selectQuality']"
DOWNLOAD_URL_X_PATH_DEFAULT = DOWNLOAD_URL_X_PATH + "/option[1]/@value"
DOWNLOAD_NAME = "//div[@id='divFileName']/b/following::node()"

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


def getOpenLoadUrls(link, ses, sleeptime, verbose=False):
    #deprecated!
    time.sleep(sleeptime)

    payload = {"s": "openload"}

    mu.acquire()
    html_raw = ses.get(link, params=payload)
    mu.release()

    html_str = html_raw.content

    lxml_parse = html.fromstring(html_str)

    # Selected server option
    SEL_SER_OPT = "//select[@id='selectServer']/option[text()='Openload']"
    if(len(lxml_parse.xpath(SEL_SER_OPT)) == 0):
        return False

    find_str = r"""src=\"https?:\/\/openload.co(.*?)\""""

    try:
        raw_data = re.search(find_str, html_str).group(1)
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find '" + find_str +
                 "'", Color.RED, Color.BOLD)
        return False
    except TypeError:
        raw_data = re.search(find_str, html_str.decode(
            html_raw.encoding)).group(1)
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: " + find_str, Color.RED, Color.BOLD)
        return False

    raw_data = "https://openload.co" + raw_data

    mu.acquire()
    temp_r = ses.get(raw_data)
    mu.release()

    lxml_parse = html.fromstring(temp_r.content)

    hiddenurl_xpath = "//*[@id='hiddenurl']/text()"
    deobfuscatedaa = jsdecode2(lxml_parse.xpath(hiddenurl_xpath)[0])

    deobfuscatedaa = "https://openload.co/stream/" + deobfuscatedaa

    mu.acquire()
    temp_head = ses.head(deobfuscatedaa)
    mu.release()

    # openload now redirects
    redirect = temp_head.headers['location']

    file_name = unquote(redirect).rpartition('/')[-1]

    if(verbose):
        print_mu.acquire()
        print("Found download link: " + redirect)
        uprint("Found file name: " + file_name)
        print_mu.release()

    return [file_name, redirect, link]

def getBlogspotUrls(link, ses, sleeptime, quality_txt, verbose=False):
    genned_x_path = DOWNLOAD_URL_X_PATH

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
    raw_data = temp_tree.xpath(DOWNLOAD_NAME)

    if(len(raw_data) == 0):
        return False

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

    discovered_url = ""

    if("/Anime/" in link):
        # site is kissanime
        discovered_url = kissencAnime(temp_tree.xpath(dl_url_x_path)[0])
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
        return False

    if(verbose):
        print_mu.acquire()
        uprint("Found download link: " + discovered_url)
        uprint("Found file name: " + format_txt)
        print_mu.release()

    return [format_txt, discovered_url, link]