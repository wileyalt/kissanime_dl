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

#unicode colors!
class Color:
	BEG = '\033['
	SEP = ';'
	BOLD = '1'
	RED = '31'
	GREEN = '32'
	END_BEG = 'm'
	END = '\033[0m'

def printClr(string, *args):
	#we have to work backwards
	string = Color.END_BEG + string

	fst = False
	for arg in args:
		if(fst == False):
			string = arg + string
			fst = True
			continue

		string = Color.SEP + string
		string = arg + string

	string = Color.BEG + string
	print(string + Color.END)

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
	printClr("An optional argument is --verbose", Color.BOLD)
	printClr("An optional argument is --simulate.", Color.BOLD)
	print("    This simulates finding the links, but doesn't download")
	printClr("An optional argument is --episode=BEG%OPT_END.", Color.BOLD)
	print("    If only one number is given, then only that one episode is downloaded")
	print("    The BEG episode MUST BE the one at the top of the page")
	print("    Defaults to all")
	printClr("An optional argument is ---max_threads=VAL.", Color.BOLD)
	print("    Val is the number of threads to SEARCH for the download links")
	print("    Defaults to 5")
	print("    Downloading the files uses one thread per file and CANNOT be changed")
	printClr("--help prints this message", Color.BOLD)

def main():
	#beginning clock
	start_time = time.time()
	plat = platform.system()
	print("Platform: " + plat)
	if(len(sys.argv) < 3):
		printClr("Error: kissanime_dl takes in 2 args, the url, and the path to download to", Color.BOLD, Color.RED)
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
	simulate = False
	episode_range = []
	MAX_THREADS = 5
	
	#optional args
	if(len(sys.argv) > 3):
		for i in range (3, len(sys.argv) ):
			psd_arg = sys.argv[i]
			if(psd_arg.split('=')[0] == "--verbose"):
				verbose = True
			elif(psd_arg.split('=')[0] == "--simulate"):
				simulate = True
			elif(psd_arg.split('=')[0] == "--help"):
				printError()
				return
			elif(psd_arg.split('=')[0] == "--episode"):
				eps = psd_arg.split('=')[1].replace(' ', '').split('%')
				first = ''
				second = ''
				if(len(eps) == 1):
					first = eps[0]
					if(first == ''):
						printClr("Error: The first argument cannot be blank", Color.BOLD, Color.RED)
						printError()
						return

					while(len(first) < 3):
						first = "0" + first

				elif(len(eps) == 2):
					first = eps[0]
					while(len(first) < 3):
						first = "0" + first
					second = eps[1]
					while(len(second) < 3):
						second = "0" + second

				EPS_PREFIX = "Episode-"
				if(EPS_PREFIX not in first and len(first) == 3):
					first = EPS_PREFIX + first
				if(EPS_PREFIX not in second and len(second) == 3 and len(eps) == 2):
					second = EPS_PREFIX + second

				episode_range = [first, second]

				if verbose:
					print("Searching for episodes between: " + episode_range[0] + " and " + episode_range[1])

			else:
				printClr("Unknown argument: " + sys.argv[i], Color.BOLD, Color.RED)
				printError()
				return;

	#begin session
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
		printClr(url + "does not go to kissanime.to!", Color.BOLD, Color.RED)
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

	URL_ERROR_URL = "https://kissanime.to/Error"
	if(r.url == URL_ERROR_URL):
		printClr("Url error at " + url, Color.BOLD, Color.RED)
		print("Check your url and try again")
		return

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

	escapes = ''.join([chr(char) for char in range(1, 32)])
	def getDLUrls(queuee, links, ses):
		for ur in links:
			mu.acquire()
			temp_r = ses.get(ur)
			mu.release()
			temp_tree = html.fromstring(temp_r.content)
			raw_data = temp_tree.xpath(DOWNLOAD_NAME)
			if(len(raw_data) == 0):
				print("Failed to grab url")
				if verbose:
					print(temp_r.content)
				print("You may have to open a browser and manually verify capcha")
				return
			#             NAME                            DOWNLOAD_URL
			format_txt = raw_data[0].replace(" ", '').translate(None, escapes)
			queuee.put([format_txt, wrap(temp_tree.xpath(DOWNLOAD_URL_X_PATH)[0].value_options[0])])
			if verbose:
				print_mu.acquire()
				print("Found download link: " + wrap(temp_tree.xpath(DOWNLOAD_URL_X_PATH)[0].value_options[0] ) )
				print("Found file name: " + format_txt)
				print_mu.release()

	if verbose:
		print vid_links

	if(len(episode_range) > 0):
		rm_links = []

		if verbose:
			print("Removing episodes")
		for ln in vid_links:
			frmt_ln = ln.split("/")[-1].split("?")[0]
			if(episode_range[0] not in frmt_ln):
				if verbose:
					print("Removed link: " + ln)
				rm_links.append(ln)
			else:
				break

		if(episode_range[1] != ''):
			for ln in reversed(vid_links):
				frmt_ln = ln.split("/")[-1].split("?")[0]
				if(episode_range[1] not in frmt_ln):
					rm_links.append(ln)
				else:
					break

		elif(episode_range[1] == ''):
			for ln in reversed(vid_links):
				frmt_ln = ln.split("/")[-1].split("?")[0]
				if(episode_range[0] not in frmt_ln):
					rm_links.append(ln)

		for ln in rm_links:
			if verbose:
				print("Removed link: " + ln)
			vid_links.remove(ln)


	if(len(vid_links) < MAX_THREADS):
		MAX_THREADS = len(vid_links)

	CHUNK_SIZE = len(vid_links) / MAX_THREADS
	dl_urls = Queue.Queue()
	thrs = []
	for i in range(MAX_THREADS):
		if verbose:
			print("Creating Thread " + str(i) )
		loc_data = []
		if(i == MAX_THREADS - 1):
			loc_data = vid_links[(i * CHUNK_SIZE) : ]
		else:
			loc_data = vid_links[(i * CHUNK_SIZE) : (i * CHUNK_SIZE + CHUNK_SIZE)]
		if verbose:
			print(loc_data)
		thrs.append(threading.Thread(target = getDLUrls, args = (dl_urls, loc_data, sess) ) )
		thrs[i].Daemon = True
		thrs[i].start()

	for i in range(MAX_THREADS):
		thrs[i].join()

	del thrs

	if(simulate):
		end_time = time.time()
		print("Finished simulation")
		printClr("Found " + str(len(vid_links) ) + " links", Color.BOLD, Color.GREEN)
		printClr("Elapsed time: " + str(timedelta(seconds = (end_time - start_time) ) ), Color.BOLD)
		return

	thrs = []

	#more threads to start downloading
	for i in range(len(vid_links) ):
		thrs.append(threading.Thread(target = downloadFile, args = (dl_urls, dl_path) ) )
		thrs[i].Daemon = True
		thrs[i].start()

	for th in thrs:
		th.join()

	end_time = time.time()
	printClr("Downloaded " + len(vid_links) + "files at " + dl_path, Color.BOLD, Color.GREEN)
	printClr("Elapsed time: " + str(timedelta(seconds = (end_time - start_time) ) ), Color.BOLD)

main()