# -*- coding: utf-8 -*-

from lxml import html
import requests
import re
import time

try:
    # python2
    from urlparse import urlparse
except ImportError:
    # python3
    from urllib.parse import urlparse

try:
    from color_print import Color, printClr
except ImportError:
    from .color_print import Color, printClr

try:
    from jsexec import convJStoPy
except ImportError:
    from .jsexec import convJStoPy


def findBetween(string, start, end):
    return string[string.find(start) + len(start): string.rfind(end)]


def makeSession(url, vurl_result, verbose):
    # begin session
    sess = requests.Session()
    sess.keep_alive = True
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

    r = sess.get(url, timeout=30.0)
    if verbose:
        print("Started session at " + url)

    if(r.status_code != requests.codes.ok and r.status_code != 503):
        # Bad connection to site
        printClr("Failed to get a good status code with site",
                 Color.BOLD, Color.RED)
        return

    tree = html.fromstring(r.content)
    script = findBetween(r.text, "<script", "</script>")
    strip_script = [stri.strip() for stri in script.splitlines()]

    js_var_t = "<a href='/'>x</a>"
    # root("/") url
    js_var_t_href = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))

    try:
        js_var_r = re.search(r"https?:\/\/", js_var_t_href).group(0)
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find 'https?:\/\/' in " +
                 js_var_t_href, Color.RED, Color.BOLD)
        raise
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: https?:\/\/", Color.RED, Color.BOLD)
        raise

    js_var_t = js_var_t_href[len(js_var_r):]
    js_var_t = js_var_t[0: len(js_var_t) - 1]

    val_jschl_vc = tree.xpath("//input[contains(@name, 'jschl_vc')]")[0].value
    val_pass = tree.xpath("//input[contains(@name, 'pass')]")[0].value

    string_to_eval_re_search = "[^ ]+$"
    try:
        string_to_eval = "var " + \
            re.search(string_to_eval_re_search, strip_script[8]).group(0)
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find " + string_to_eval_re_search +
                 " in " + strip_script[8], Color.RED, Color.BOLD)
        raise
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: " + string_to_eval_re_search, Color.RED, Color.BOLD)
        raise

    another_regex_str = "^(.*)(?:a.value)"
    try:
        string_to_eval = string_to_eval + \
            re.search(another_regex_str, strip_script[15]).group(1)[1:]
    except AttributeError as e:
        printClr("Regex Failure", Color.RED, Color.BOLD)
        printClr("Could not find " + another_regex_str +
                 " in " + strip_script[15], Color.RED, Color.BOLD)
        raise
    except:
        printClr("Unknown Regex Error", Color.RED, Color.BOLD)
        printClr("Pattern: " + another_regex_str, Color.RED, Color.BOLD)
        raise

    val_unkwn_var = convJStoPy(string_to_eval) + len(js_var_t)

    payload = {
        'jschl_vc': val_jschl_vc,
        'pass': val_pass,
        'jschl_answer': val_unkwn_var
    }

    print("Waiting for authentication...")
    print("Should take about 4 seconds")
    # wait for 4 sec
    time.sleep(4)

    URL_SEND_PAYLOAD_TO = vurl_result[0] + "/cdn-cgi/l/chk_jschl"
    form_get = sess.get(URL_SEND_PAYLOAD_TO, params=payload, timeout=30.0)

    if(form_get.status_code != requests.codes.ok):
        raise RuntimeError("Converting the CloudFlare JS has changed!")

    return sess
