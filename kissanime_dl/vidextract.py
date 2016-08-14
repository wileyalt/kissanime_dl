# -*- coding: utf-8 -*-
# By WILEY YU

import time
import re
import threading
import sys

import requests
from lxml import html

try:
    from kissenc import kissencCartoon, kissencAsian, kissencAnime
except ImportError:
    from .kissenc import kissencCartoon, kissencAsian, kissencAnime

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

def getOpenLoadUrls(link, ses, sleeptime, verbose=False):
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

    print('a')

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

    raw_data = "http://openload.co" + raw_data
    raw_data = raw_data.replace("embed", "f")

    mu.acquire()
    temp_r = ses.get(raw_data)
    mu.release()

    try:
        aaencoded = re.search(">ﾟωﾟﾉ= (.*?) \('_'\);",
                              temp_r.content).group(1)
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find '>ﾟωﾟﾉ= (.*?) \('_'\);' in " +
                 raw_data, Color.RED, Color.BOLD)
        return False
    except TypeError:
        aaencoded = re.search(">ﾟωﾟﾉ= (.*?) \('_'\);",
                              temp_r.text).group(1)
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: >ﾟωﾟﾉ= (.*?) \('_'\);", Color.RED, Color.BOLD)
        return False

    # need to add beginning and ending face to complete the encoded string
    aaencoded = "ﾟωﾟﾉ= " + aaencoded + " ('_');"

    decodedaa = decodeAA(aaencoded)

    try:
        decodedaa = re.search("function\(\)(.*)\(\)", decodedaa).group(1)
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find 'function\(\)(.*)\(\)' in " +
                 decodedaa, Color.RED, Color.BOLD)
        return False
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: function\(\)(.*)\(\)", Color.RED, Color.BOLD)
        return False

    # need to add function call and anonymous function
    decodedaa = "function()" + decodedaa + "();"

    # sometimes there are double +?
    decodedaa = decodedaa.replace("++", "+")

    try:
        decodedaa = re.search(".*(return)(.*)}", decodedaa).group(2)
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find '.*(return)(.*)}' in " +
                 decodedaa, Color.RED, Color.BOLD)
        return False
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: .*(return)(.*)}", Color.RED, Color.BOLD)
        return False

    decodedaa = decodedaa.replace(" ", '')
    decodedaa = decodedaa.replace("\n", '')

    deobfuscatedaa = decodeFunky(decodedaa)

    mu.acquire()
    temp_head = requests.head(deobfuscatedaa)
    mu.release()

    # openload now redirects
    redirect = temp_head.headers['location']

    print(unquote(redirect))

    file_name = unquote(redirect).rpartition('/')[-1]

    print(file_name)

    if(verbose):
        print_mu.acquire()
        print("Found download link: " + redirect)
        print("Found file name: " + file_name)
        print_mu.release()

    return [file_name, redirect, link]

def getBlogspotUrls(link, ses, sleeptime, quality_txt, verbose=False):
    if(quality_txt != ""):
        DOWNLOAD_URL_X_PATH = DOWNLOAD_URL_X_PATH + \
            "/option[normalize-space(text() ) = \'" + \
            quality_txt + "\']/@value"
    else:
        # defaults to highest quality
        DOWNLOAD_URL_X_PATH = DOWNLOAD_URL_X_PATH_DEFAULT

    time.sleep(sleeptime)

    # lets make a copy
    dl_url_x_path = DOWNLOAD_URL_X_PATH

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
        print("Found download link: " + discovered_url)
        print("Found file name: " + format_txt)
        print_mu.release()

    return [format_txt, discovered_url, link]