#By WILEY YU

import sys
import platform
import os.path
import Queue
import re
import Queue
import threading
import time
import shutil
from urlparse import urlparse
from datetime import timedelta

import requests
from lxml import html

NAME = 0
DOWNLOAD_URL = 1

console_mu = threading.Lock()
def downloadFile(queue, dl_path):
	url = queue.get()
	dl_name = unicode(url[NAME])
	if(len(dl_name) > 252):
		dl_name = dl_name[:252]

	console_mu.acquire()
	print("Beginning to download " + dl_name)
	console_mu.release()
	data = requests.get(url[DOWNLOAD_URL], stream = True)
	with open(dl_path + "/" + dl_name + ".mp4", 'wb') as dl_file:
		shutil.copyfileobj(data.raw, dl_file)
	del data
	console_mu.acquire()
	print("Finished downloading " + dl_name)
	console_mu.release()
	return

def findBetween(string, start, end):
	return string[string.find(start) + len(start) : string.rfind(end)]

def convJStoPy(string):
	conv = string.replace("!![]", "1")
	conv = conv.replace("!+[]", "1")
	conv = conv.replace("[]", "0")
	conv = conv.replace("+", "", 0)
	conv = conv.replace("((", "int(str(")
	conv = conv.replace(")+(", ")+str(")
	return conv

def wrap(string):
	alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
	lookup = {}
	def fromUTF8(string):
		pos = -1
		leng = 0
		buff = []
		enc = [0] * 4
		if(len(lookup) == 0):
			leng = len(alphabet)
			while(pos < leng - 1):
				pos += 1
				lookup[alphabet[pos]] = pos
			pos = -1
		leng = len(string)
		while(pos < leng):
			try:
				pos += 1 #++pos
				if(pos == leng):
					break
				enc[0] = lookup[string[pos] ]
				pos += 1 #++pos
				enc[1] = lookup[string[pos] ]
				buff.append((enc[0] << 2) | (enc[1] >> 4) )
				pos += 1 #++pos
				enc[2] = lookup[string[pos] ]
				if(enc[2] == 64):
					break
				buff.append(((enc[1] & 15) << 4) | (enc[2] >> 2))
				pos += 1 #++pos
				enc[3] = lookup[string[pos] ]
				if(enc[3] == 64):
					break
				buff.append(((enc[2] & 3) << 6) | enc[3])
			except:
				print(string)
				print(leng)
				print(pos)
				print(string[pos])
				raise

		return buff

	if(len(string) % 4):
		print("Wrap failed")
		return

	buff = fromUTF8(string)
	position = 0
	leng = len(buff)

	result = ''
	while(position < leng):
		if(buff[position] < 128):
			result += unichr(buff[position])
			position += 1
		elif(buff[position] > 191 and buff[position] < 224):
			first = ((buff[position] & 31) << 6)
			position += 1
			second = (buff[position] & 63)
			position += 1
			result += unichr(first | second);
		else:
			first = ((buff[position] & 15) << 12)
			position += 1
			second = ((buff[position] & 63) << 6)
			position += 1
			third = (buff[position] & 63)
			position += 1
			result += unichr(first | second | third)

	return ''.join(result)

def printError():
	print("Error: kissanime_dl takes in 2 args, the url, and the path to download to")
	print("An optional argument is --verbose")

def main():
	#beginning clock
	start_time = time.time()
	plat = platform.system()
	print("Platform: " + plat)
	if(len(sys.argv) > 4 or len(sys.argv) < 3):
		printError()
		return

	url = sys.argv[1]
	if(requests.head(url).status_code != requests.codes.ok and requests.head(url).status_code != 503):
		print(url + " is not a valid url!")
		printError()
		return

	dl_path = sys.argv[2]

	if(os.path.isdir(dl_path) == False):
		print(dl_path + " is not a valid directory to download to")
		printError()
		return

	verbose = False
	
	if(len(sys.argv) > 3):
		for i in range (3, len(sys.argv) ):
			psd_arg = sys.argv[i]
			if(psd_arg.split('=')[0] == "--verbose"):
				verbose = True
			else:
				print("Unknown argument: " + sys.argv[i])
				return;

	sess = requests.Session()
	sess.keep_alive = True
	r = sess.get(url)
	if verbose:
		print("Started session at " + url)
	tree = html.fromstring(r.content)
	script = findBetween(r.text, "<script", "</script>")
	strip_script = [stri.strip() for stri in script.splitlines()]

	#We need to decode the javascript
	#f is the last known variable before the messy one
	#starts ln 9
	var_beg = "f, "
	var_end = "="
	json_name_beg = "\""
	json_name_end = "\""
	json_data_beg = ":"
	json_data_end = "}"

	unkwn_var_name = findBetween(strip_script[8], var_beg, var_end) + "." + findBetween(strip_script[8], json_name_beg, json_name_end) 
	val_unkwn_var = eval(convJStoPy(findBetween(strip_script[8], json_data_beg, json_data_end) ) )

	js_var_t = "<a href='/'>x</a>"
	#root("/") url
	js_var_t_href = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))

	if("https://kissanime.to" not in js_var_t_href):
		print(url + "does not go to kissanime.to!")
		printError()
		return

	js_var_r = re.search(r"https?:\/\/", js_var_t_href).group(0)

	js_var_t = js_var_t_href[len(js_var_r) :]
	js_var_t = js_var_t[0 : len(js_var_t) - 1]

	val_jschl_vc = tree.xpath("//input[contains(@name, 'jschl_vc')]")[0].value
	val_pass = tree.xpath("//input[contains(@name, 'pass')]")[0].value

	#splits code into bite-size array
	#operations are at line 16
	var_complex_op = [stri+";" for stri in strip_script[15].split(";")]

	for string in var_complex_op[:-2]:
		if unkwn_var_name not in string:
			continue
		else:
			eval_phrase = "val_unkwn_var" + findBetween(string, unkwn_var_name, "=") + "(" + convJStoPy(findBetween(string, '=', ';') ) + ")"
			#print(eval_phrase)
			#print("genned val: " + str(eval("(" + convJStoPy(findBetween(string, '=', ';') ) + ")") ) )
			val_unkwn_var = eval(eval_phrase)

	val_unkwn_var = val_unkwn_var + len(js_var_t)

	payload = {
		'jschl_vc' : val_jschl_vc,
		'pass' : val_pass,
		'jschl_answer' : val_unkwn_var
	}

	print("Waiting for authentication...")
	#wait for 4 sec
	time.sleep(4)

	URL_SEND_PAYLOAD_TO = "https://kissanime.to/cdn-cgi/l/chk_jschl"
	sess.get(URL_SEND_PAYLOAD_TO, params=payload)

	r = sess.get(url)
	tree = html.fromstring(r.content)

	LINK_TABLE_X_PATH = "//table[@class='listing']/tr/td/a"
	vid_lxml_ele = tree.xpath(LINK_TABLE_X_PATH)

	vid_links = []
	for i in range(len(vid_lxml_ele) ):
		vid_links.append(js_var_t_href[:-1] + vid_lxml_ele[i].attrib['href'])
		if verbose:
			print("Found link: " + js_var_t_href[:-1] + vid_lxml_ele[i].attrib['href'])


	DOWNLOAD_URL_X_PATH = "//select[@id='selectQuality']"
	DOWNLOAD_NAME = "//div[@id='divFileName']/b/following::node()"
	mu = threading.Lock()
	print_mu = threading.Lock()
	def getDLUrls(queuee, links, ses):
		for ur in links:
			mu.acquire()
			temp_r = ses.get(ur)
			mu.release()
			temp_tree = html.fromstring(temp_r.content)
			escapes = ''.join([chr(char) for char in range(1, 32)])

			#             NAME                            DOWNLOAD_URL
			format_txt = temp_tree.xpath(DOWNLOAD_NAME)[0].replace(" ", '').translate(None, escapes)
			queuee.put([format_txt, wrap(temp_tree.xpath(DOWNLOAD_URL_X_PATH)[0].value_options[0])])
			if verbose:
				print_mu.acquire()
				print("Found download link: " + wrap(temp_tree.xpath(DOWNLOAD_URL_X_PATH)[0].value_options[0] ) )
				print("Found file name: " + format_txt)
				print_mu.release()

	MAX_THREADS = 5
	CHUNK_SIZE = len(vid_lxml_ele) / MAX_THREADS
	dl_urls = Queue.Queue()
	thrs = []
	for i in range(MAX_THREADS):
		if verbose:
			print("Creating Thread " + str(i) )
		loc_data = []
		if(i == MAX_THREADS - 1):
			loc_data = vid_links[(i * MAX_THREADS) : -1]
		else:
			loc_data = vid_links[(i * MAX_THREADS) : (i * MAX_THREADS + MAX_THREADS)]
		thrs.append(threading.Thread(target = getDLUrls, args = (dl_urls, loc_data, sess) ) )
		thrs[i].Daemon = True
		thrs[i].start()

	for i in range(MAX_THREADS):
		thrs[i].join()

	del thrs

	thrs = []

	#more threads to start downloading
	for i in range(len(vid_links) ):
		thrs.append(threading.Thread(target = downloadFile, args = (dl_urls, dl_path) ) )
		thrs[i].Daemon = True
		thrs[i].start()

	for th in thrs:
		th.join()

	end_time = time.time()
	print("Downloaded " + len(vid_links) + "files at " + dl_path)
	print("Elapsed time: " + str(timedelta(seconds = (end_time - start_time) ) ) )

main()