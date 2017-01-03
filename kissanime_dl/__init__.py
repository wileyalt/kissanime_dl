# -*- coding: utf-8 -*-
# By WILEY YU

import sys
import platform
import pip
import os.path
import string
import re
import threading
import time
import shutil
import json

from datetime import timedelta
try:
    # python2
    from Queue import Queue
except ImportError:
    # python3
    from queue import Queue

try:
    # python2
    from urlparse import urlparse
except ImportError:
    # python3
    from urllib.parse import urlparse

import requests
from lxml import html

try:
    from version import __version__
except ImportError:
    from .version import __version__

try:
    from session_make import makeSession
except ImportError:
    from .session_make import makeSession

try:
    from validhead import valid_begin, valid_end
except ImportError:
    from .validhead import valid_begin, valid_end

try:
    from color_print import Color, printClr
except ImportError:
    from .color_print import Color, printClr

try:
    from jsexec import convJStoPy
except ImportError:
    from .jsexec import convJStoPy

try:
    from vidextract import getOpenLoadUrls, getBlogspotUrls
except ImportError:
    from .vidextract import getOpenLoadUrls, getBlogspotUrls

url = ''
JSON_HIS_MASTER_LINK_KEY = "master_link"
JSON_HIS_VID_LINKS_KEY = "vid_links"

# GOTTA GET THAT VERSION
# Get python version
PYTHON_VER = sys.version_info[0]

NAME = 0
DOWNLOAD_URL = 1
PARENT_URL = 2

console_mu = threading.Lock()
write_hist = threading.Lock()


def autoUpdate():
    printClr("Checking for updates", Color.BOLD)
    pip.main(['install', '-U', '--no-cache-dir', '--no-deps', 'kissanime_dl'])


def printCaptchaWarning():
    printClr("""Warning: Version 1.9.6 changed the host of kisscartoon.me to kisscartoon.se.""",
             Color.BOLD, Color.YELLOW)

def clearAndWriteHistory(urls_arr, PATH_TO_HISTORY, masterurl):
    json_his_data = {JSON_HIS_MASTER_LINK_KEY: masterurl}
    json_his_data[JSON_HIS_VID_LINKS_KEY] = urls_arr

    with open(PATH_TO_HISTORY, 'w') as f_data:
        json.dump(json_his_data, f_data)


def writeHistory(urls_arr, PATH_TO_HISTORY, masterurl):
    # lets write that history file!
    link_history_data = {}

    # open that file
    # reads file no matter what
    if(os.path.isfile(PATH_TO_HISTORY)):
        with open(PATH_TO_HISTORY) as f:
            link_history_data = json.load(f)

    json_his_data = {JSON_HIS_MASTER_LINK_KEY: masterurl}

    # not update
    if(len(link_history_data) == 0):
        json_his_data[JSON_HIS_VID_LINKS_KEY] = urls_arr
    else:
        # is update
        temp_data = link_history_data[JSON_HIS_VID_LINKS_KEY]
        for lnk in urls_arr:
            temp_data.append(lnk)

        json_his_data[JSON_HIS_VID_LINKS_KEY] = temp_data
    with open(PATH_TO_HISTORY, 'w') as f_data:
        json.dump(json_his_data, f_data)


# cross version
def cVunicode(any):
    if isinstance(any, str) and sys.version_info < (3, 0, 0):
        return any.encode('utf-8').strip()
    return any
	
# cross version of printing unicode
def uprint(any):
    try:
        any.encode(sys.stdout.encoding)
        if isinstance(any, str) and sys.version_info < (3, 0, 0):
            print(any.encode('utf-8').strip() )
            return
        print(any)
    except UnicodeEncodeError:
        return "Unsupported characters in " + sys.stdout.encoding

def downloadFile(url, dl_path, PATH_TO_HISTORY, masterurl, should_autogen):

    if(should_autogen):
        dl_name = cVunicode(url[PARENT_URL].split('/')[-1].split('?')[0])
    else:
        dl_name = cVunicode(url[NAME])

    dl_path = cVunicode(dl_path)

    if(not isinstance(dl_name, str) and not isinstance(dl_name, unicode)):
        # incase any strange happenings happen with extracting the filename
        dl_name = url[DOWNLOAD_URL].split('/')[-1]

    if(len(dl_name) > 252):
        dl_name = dl_name[:252]

    f_name = dl_path + "/" + dl_name + ".mp4"
    size = 0

    if(os.path.isfile(f_name)):
        size = os.path.getsize(f_name)
        console_mu.acquire()
        uprint("Resuming download of " + dl_name)
        console_mu.release()
    else:
        console_mu.acquire()
        uprint("Beginning to download " + dl_name)
        console_mu.release()

    # Range Header prepare
    # For resuming downloads
    range_header = {'Range': 'bytes=%d-' % size}
    data = requests.get(url[DOWNLOAD_URL], headers=range_header, stream=True)

    type_of_file_op = ''

    # Check to see if partial content status code is sent back
    if(data.status_code == 206):
        type_of_file_op = "ab"
    else:
        type_of_file_op = "wb"

    with open(f_name, type_of_file_op) as dl_file:
        shutil.copyfileobj(data.raw, dl_file)
    del data

    # write to data immediately to save
    write_hist.acquire()
    writeHistory([url[PARENT_URL]], PATH_TO_HISTORY, masterurl)
    write_hist.release()

    console_mu.acquire()
    uprint("Finished downloading " + dl_name)
    console_mu.release()

def printError():
    printClr("The first argument is the url or update", Color.BOLD)
    print("    'update' can only be given if kissanime_dl has been run in that directory before")
    print("    The url can be from kissanime.ru, kisscartoon.se, and kissasian.com")
    printClr(
        "The second argument is the path to download to or '-' which auto creates a directory for you", Color.BOLD)
    printClr("An optional argument is --verbose", Color.BOLD)
    printClr("An optional argument is --simulate", Color.BOLD)
    print("    This simulates finding the links, but doesn't download")
    printClr("An optional argument is --episode=OPT_BEG%OPT_END", Color.BOLD)
    print("    If only OPT_BEG is given WITHOUT '%', only one episode will be downloaded")
    print("    If only OPT_BEG is given WITH '%', then all files after OPT_BEG will be downloaded")
    print("    If only OPT_END is given WITH '%', then all files before OPT_END will be downloaded")
    print("    If OPT_BEG and OPT_END is given, then a range between the two will be downloaded")
    print("    '%'' literal needs to be between the two")
    print("    OPT_BEG needs to be above OPT_END in terms of the page (usually from largest to smallest)")
    print("    Defaults to all")
    printClr("An optional argument is --quality=QUAL", Color.BOLD)
    print("    This sets the quality of the video download")
    printClr("An optional argument is --txtlinks", Color.BOLD)
    print("    This creates a txt file with the links to the videos, but does not download them")
    printClr("An optional argument is --forcehistory", Color.BOLD)
    print("    Forces a history to be written with the given episodes")
    print("    This is good for manually setting files you don't want to download when updating")
    printClr("An optional argument is --noupdate", Color.BOLD)
    print("    Prevents the program from checking for and updating to the newest version of kissanime_dl")
    printClr("An optional argument is --delay=SEC", Color.BOLD)
    print("    Sets the delay in seconds between requests to the url given in the first argument.")
    printClr("An optional argument is --legacy", Color.BOLD)
    print("    It runs the script in legacy mode")
    printClr("An optional argument is --autogen", Color.BOLD)
    print("    It names the episodes numerically, rather than the filename")
    printClr("An optional argument is --help", Color.BOLD)


def getElapsedTime(s_time):
    end_time = time.time()
    return str(timedelta(seconds=(end_time - s_time)))


# MAIN
def main(args):
    LINK_HISTORY_FILE_NAME = "kissanime_dl_history.json"
    # Json data should look like this:
    # [
    # "master_link" : MASTER_LINK,
    # "vid_links" : [VID_LINKS]
    # ]
    # beginning clock
    start_time = time.time()
    plat = platform.system()
    print("Platform: " + plat)
    print("Python Version: " + str(PYTHON_VER))
    printClr("Program Version: " + __version__, Color.BOLD)

    verbose = False
    simulate = False
    txtlinks = False
    forcehistory = False
    openload = False
    auto_update = True
    run_legacy = False
    auto_gen = False

    episode_range = []
    episode_range_single = False

    MAX_THREADS = 5
    quality_txt = ""

    sleepy_time = 0.1

    # print that captcha warning
    printCaptchaWarning()

    if(len(args) < 2):
        printClr("Error: kissanime_dl takes in 2 args, the url, and the path to download to",
                 Color.BOLD, Color.RED)
        printError()
        return

    # gets first arg
    url = args[0]

    # optional args
    if(len(args) > 2):
        for i in range(2, len(args)):
            psd_arg = args[i]
            case_arg = psd_arg.split('=')[0]
            if(case_arg == "--verbose"):
                verbose = True
            elif(case_arg == "--simulate"):
                simulate = True
            elif(case_arg == "--txtlinks"):
                txtlinks = True
            elif(case_arg == "--help"):
                printError()
                return
            elif(case_arg == "--episode"):
                eps = psd_arg.split('=')[1].replace(' ', '')
                first = ''
                second = ''
                if('%' not in eps):
                    #if only one episode download
                    episode_range_single = True
                    first = eps
                    second = "000"

                else:
                    #range of downloads
                    eps = eps.split('%')
                    if(len(eps) == 1):
                        first = eps[0]
                        if(first == ''):
                            printClr(
                                "Error: The arguments cannot be blank", Color.BOLD, Color.RED)
                            printError()
                            return

                        second = "000"

                    elif(len(eps) == 2):
                        first = eps[0]
                        second = eps[1]
                        if(first == "000" and second == "000"):
                            printClr(
                                "Error: Both arguments cannot be blank", Color.BOLD, Color.RED)
                            printError()
                            return

                while(len(first) < 3 and "kissasian" not in url):
                    first = "0" + first

                while(len(second) < 3 and "kissasian" not in url):
                        second = "0" + second

                EPS_PREFIX = "Episode-"
                if(EPS_PREFIX not in first):
                    first = EPS_PREFIX + first
                if(EPS_PREFIX not in second):
                    second = EPS_PREFIX + second

                episode_range = [first, second]

                if(verbose and not episode_range_single):
                    print("Searching for episodes between: " +
                          episode_range[0] + " and " + episode_range[1])
                elif(verbose and episode_range_single):
                    print("Searching for episode: " + episode_range[0])

            elif(case_arg == "--max_threads"):
                str_val = psd_arg.split('=')[1]
                if(not str_val.isdigit()):
                    printClr(
                        "Error: " + str_val + " is not a valid value for threading", Color.BOLD, Color.RED)
                    return

                MAX_THREADS = int(psd_arg.split('=')[1])

                if(MAX_THREADS < 1):
                    printClr("Error: Cannot have max threads less than 1",
                             Color.BOLD, Color.RED)
                    return

            elif(case_arg == "--quality"):
                quality_txt = psd_arg.split('=')[1]
                if(not quality_txt.isdigit() and quality_txt[:-1] is not 'p'):
                    printClr("Error: " + quality_txt +
                             " is not a numerical value", Color.BOLD, Color.RED)
                    return

                if(quality_txt.isdigit() and quality_txt[:-1] is not 'p'):
                    quality_txt = quality_txt + 'p'

            elif(case_arg == "--forcehistory"):
                forcehistory = True

            elif(case_arg == "--openload"):
                openload = True

            elif(case_arg == "--noupdate"):
                auto_update = False

            elif(case_arg == "--delay"):
                sleepy_time = float(psd_arg.split('=')[1])

            elif(case_arg == "--legacy"):
                run_legacy = True

            elif(case_arg == "--autogen"):
            	auto_gen = True

            else:
                printClr("Unknown argument: " +
                         args[i], Color.BOLD, Color.RED)
                printError()
                return

    # check for updates
    if auto_update:
        autoUpdate()

    if(args[1] == '-'):
        splits = url.split('/')
        dl_dir = splits[-1] if splits[-1] else splits[-2]
        dl_path = os.path.abspath(dl_dir)
    else:
        dl_path = os.path.abspath(args[1])

    PATH_TO_HISTORY = dl_path + "/" + LINK_HISTORY_FILE_NAME

    if(os.path.isfile(dl_path)):
        printClr("File with same name exists: " +
                 dl_path, Color.BOLD, Color.RED)
        printError()
        return
    elif(not os.path.isdir(dl_path)):
        os.mkdir(dl_path)

    if(url == "update"):
        # grab the urls
        # if update is passed in

        # check if update file exists
        if(not os.path.isfile(PATH_TO_HISTORY)):
            printClr("Cannot update videos when kissanime_dl has never been run at " +
                     dl_path, Color.BOLD, Color.RED)
            printClr("Make sure that " + LINK_HISTORY_FILE_NAME +
                     " exists at that directory", Color.BOLD)
            return

    magiclink = {}

    # load update file if it exists to prevent redownloading
    if(os.path.isfile(PATH_TO_HISTORY)):
        with open(PATH_TO_HISTORY) as f:
            magiclink = json.load(f)

    if(url == "update"):
        url = magiclink[JSON_HIS_MASTER_LINK_KEY]
        if(verbose):
            print("Found url from history: " + url)

        def portHistoryFile(fromurl, tourl):
            newmagiclink = [];
            for lnk in magiclink[JSON_HIS_VID_LINKS_KEY]:
                newmagiclink.append(lnk.replace(fromurl, tourl) )

            magiclink[JSON_HIS_VID_LINKS_KEY] = newmagiclink

            #rewrite history file!
            printClr("Porting history file from " + fromurl + " to " + tourl + "!", Color.BOLD, Color.YELLOW)
            clearAndWriteHistory(newmagiclink, PATH_TO_HISTORY, url)

        if "kissanime.to" in url:
            # I want to convert all kissanime.to to kissanime.ru first
            url = url.replace("kissanime.to", "kissanime.ru")
            portHistoryFile("kissanime.to", "kissanime.ru")

        if "kisscartoon.me" in url:
            #convert kisscartoon.me to kisscartoon.se
            url = url.replace("kisscartoon.me", "kisscartoon.se")
            portHistoryFile("kisscartoon.me", "kisscartoon.se")

    # Makes sure to connect to valid-ish urls.
    vurl_result = [i for i in valid_begin if i in url]
    vurl_result += [i for i in valid_end if i in url]
    vurl_result[0] = "http://" + vurl_result[0]

    if(len(vurl_result) < 2):
        printClr(url + " is not a valid url!", Color.BOLD, Color.RED)
        return

    # Makes sure okay connection to site
    thehead = requests.head(url)
    if(thehead.status_code != requests.codes.ok and thehead.status_code != 503):
        printClr("Failed to get a good status code at " +
                 url, Color.BOLD, Color.RED)
        printClr("Status Code: " + str(thehead.status_code),
                 Color.BOLD, Color.RED)
        return

    # new session creater
    sess = makeSession(url, vurl_result, verbose)
    r = sess.get(url, timeout=30.0)

    URL_ERROR_URL = vurl_result[-1] + "/Error"
    if(r.url == URL_ERROR_URL):
        printClr("Url error at " + url, Color.BOLD, Color.RED)
        print("Check your url and try again")
        return

    if(r.status_code != requests.codes.ok):
        printClr("Error: HTTP RESPONSE CODE: " +
                 str(r.status_code), Color.BOLD, Color.RED)
        return

    printClr("Success!", Color.BOLD, Color.GREEN)

    # ASSUMING PAGE IS LOADED STARTING HERE

    tree = html.fromstring(r.content)

    LINK_TABLE_X_PATH = "//table[@class='listing']/tr/td/a"
    vid_lxml_ele = tree.xpath(LINK_TABLE_X_PATH)

    js_var_t_href = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))

    vid_links = []
    for i in range(len(vid_lxml_ele)):
        vid_links.append(js_var_t_href[:-1] + vid_lxml_ele[i].attrib['href'])
        if(verbose):
            print("Found link: " +
                  js_var_t_href[:-1] + vid_lxml_ele[i].attrib['href'])

    if(len(episode_range) > 0):
        EPISODE_NULL_TITLE = "Episode-000"

        # checks to make sure episode entered is real
        fst_ln_fnd = False
        snd_ln_fnd = False
        for ln in vid_links:
            frmt_ln = ln.split("/")[-1].split("?")[0]
            if(episode_range[0] in frmt_ln):
                fst_ln_fnd = True
            if(episode_range[1] in frmt_ln):
                snd_ln_fnd = True
            if(fst_ln_fnd and snd_ln_fnd):
                break

        if(not fst_ln_fnd and episode_range[0] != EPISODE_NULL_TITLE):
            printClr(episode_range[0] + " is not a valid episode", Color.BOLD, Color.RED)
            return

        if(not snd_ln_fnd and episode_range[1] != EPISODE_NULL_TITLE and not episode_range_single):
            printClr(episode_range[1] + " is not a valid episode", Color.BOLD, Color.RED)
            return

        rm_links = []

        if verbose:
            print("Removing episodes")

        if(episode_range[0] != EPISODE_NULL_TITLE and episode_range_single is False):
            for ln in vid_links:
                frmt_ln = ln.split("/")[-1].split("?")[0]
                if(episode_range[0] not in frmt_ln):
                    rm_links.append(ln)
                else:
                    break

        if(episode_range[1] != EPISODE_NULL_TITLE and episode_range_single is False):
            for ln in reversed(vid_links):
                frmt_ln = ln.split("/")[-1].split("?")[0]
                if(episode_range[1] not in frmt_ln):
                    rm_links.append(ln)
                else:
                    break

        #debug
        print(episode_range[0])

        if(episode_range_single):
            for ln in vid_links:
                if(episode_range[0] not in ln):
                    rm_links.append(ln)

        for ln in rm_links:
            if(verbose):
                print("Removing link: " + ln)
            if ln in vid_links:
                vid_links.remove(ln)

    # assumes first arg is update
    # checks to see if link_history_data has data in it
    if(len(magiclink) != 0):
        for lnk in magiclink[JSON_HIS_VID_LINKS_KEY]:
            if(lnk in vid_links):
                if(verbose):
                    print("Removing link: " + lnk)
                # removes link if file is in update
                vid_links.remove(lnk)

    if(len(vid_links) == 0):
        if(len(magiclink) != 0):
            printClr("No video updates found!", Color.BOLD, Color.RED)
            return

        printClr("No video links are found!", Color.BOLD, Color.RED)
        return

    if(len(vid_links) < MAX_THREADS):
        MAX_THREADS = len(vid_links)

    if(run_legacy or simulate or txtlinks):
        # Run in legacy mode
        def getDLUrls(queuee, links, ses, sleepy_time, sleepy_increment):
            count = 0
            for ur in links:
                try:
                    to_add = ""
                    if(openload is False):
                        to_add = getBlogspotUrls(ur, ses, sleepy_increment * count + sleepy_time, quality_txt, verbose)
                        if(to_add is False):
                            to_add = getOpenLoadUrls(ur, ses, sleepy_increment * count + sleepy_time, verbose)
                            if(to_add is False):
                                printClr("Failed to find url. You may have to check captcha, or KissAnime may have changed video host.", Color.RED, Color.BOLD)
                    elif(openload is True):
                        to_add = getOpenLoadUrls(ur, ses, sleepy_increment * count + sleepy_time, verbose)
                        if(to_add is False):
                            to_add = getBlogspotUrls(ur, ses, sleepy_increment * count + sleepy_time, quality_txt, verbose)
                            if(to_add is False):
                                printClr("Failed to find url. You may have to check captcha, or KissAnime may have changed video host.", Color.RED, Color.BOLD)

                    if(to_add is not False):
                        queuee.put(to_add)

                except Exception as e:
                    printClr("Error thrown while attempting to find download url: " +
                             repr(e), Color.BOLD, Color.RED)
                    print(sys.exc_info()[-1].tb_lineno)
                count += 1

        dl_urls = Queue()
        thrs = []

        try:
            # python2
            lst_to_send = [vid_links[i::MAX_THREADS] for i in xrange(MAX_THREADS)]
        except NameError:
            # python3
            lst_to_send = [vid_links[i::MAX_THREADS] for i in range(MAX_THREADS)]

        for i in range(MAX_THREADS):
            if(verbose):
                print("Creating Thread " + str(i))
            loc_data = lst_to_send[i]
            if(verbose):
                print("Data Size: " + str(len(loc_data)))
                print(loc_data)
            thrs.append(threading.Thread(target=getDLUrls, args=(
                dl_urls, loc_data, sess, sleepy_time * i + sleepy_time, sleepy_time * MAX_THREADS)))
            thrs[i].daemon = True
            thrs[i].start()

        while(threading.active_count() > 1):
            # wait one tenth of a sec
            time.sleep(0.1)

        del thrs
        del lst_to_send

        # lets clean up
        del tree
        del vid_lxml_ele
        del r
        del vid_links

        dl_urls = [item for item in dl_urls.queue]

        if(simulate):
            print("Finished simulation")
            if(forcehistory):
                writeHistory([lnk[PARENT_URL]
                              for lnk in dl_urls], PATH_TO_HISTORY, url)

            printClr("Found " + str(len(dl_urls)) +
                     " links", Color.BOLD, Color.GREEN)
            printClr("Elapsed time: " + getElapsedTime(start_time), Color.BOLD)
            return

        if(txtlinks):
            print("Finished grabbing download links")
            FILE_NAME = "Links.txt"
            FILE_PATH = dl_path + "/" + FILE_NAME

            if(forcehistory):
                writeHistory([lnk[PARENT_URL]
                              for lnk in dl_urls], PATH_TO_HISTORY, url)

            with open(FILE_PATH, 'w') as txt_data:
                for item in dl_urls:
                    txt_data.write(item[DOWNLOAD_URL] + "\n")

            printClr("Found " + str(len(dl_urls)) +
                     " links", Color.BOLD, Color.GREEN)
            printClr("Elapsed time: " + getElapsedTime(start_time), Color.BOLD)
            return

        thrs = []

        # more threads to start downloading
        lazy_programming = 0
        for dl_sing_url in dl_urls:
            thrs.append(threading.Thread(target=downloadFile, args=(
                dl_sing_url, dl_path, PATH_TO_HISTORY, url, auto_gen)))
            thrs[lazy_programming].daemon = True
            thrs[lazy_programming].start()
            lazy_programming += 1

        while(threading.active_count() > 1):
            # wait one tenth of a sec
            time.sleep(0.1)

        printClr("Downloaded " + str(len(dl_urls)) +
             " files at " + dl_path, Color.BOLD, Color.GREEN)

    else:
        # Run in new mode

        num_thrs = 5
        if(len(vid_links) < num_thrs):
            num_thrs = len(vid_links)
        dl_pool = Queue()
        for vid_url in vid_links:
            dl_pool.put(vid_url)
        thrs = []

        def getSingle(link, ses):
            pure_link = getBlogspotUrls(link, ses, sleepy_time, quality_txt, verbose)
            if(pure_link is False):
                return False
            return pure_link

        def getComplete(ses, download_pool):
            dl_link = ""

            def updatePool():
                if(not download_pool.empty()):
                    return download_pool.get()
                else:
                    return ""

            dl_link = updatePool();
            while(dl_link is not ""):
                dl_pkg = getSingle(dl_link, ses)

                if(dl_pkg is False):
                    #add back to pool
                    download_pool.put(dl_link)
                    printClr('Captcha Error @ ' + dl_link, Color.RED, Color.BOLD)
                    return

                downloadFile(dl_pkg, dl_path, PATH_TO_HISTORY, url, auto_gen)
                dl_link = updatePool()

        for i in range(num_thrs):
            thrs.append(threading.Thread(target=getComplete, args=(sess, dl_pool)))
            thrs[i].daemon = True
            thrs[i].start()

        while(threading.active_count() > 1):
            # wait one tenth of a sec
            time.sleep(0.1)

        printClr("Downloaded " + str(len(vid_links) - dl_pool.qsize()) + " files at " + dl_path, Color.BOLD, Color.GREEN)


    printClr("Elapsed time: " + getElapsedTime(start_time), Color.BOLD)
