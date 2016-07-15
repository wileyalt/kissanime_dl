# -*- coding: utf-8 -*-

#By WILEY YU

url = ''
JSON_HIS_MASTER_LINK_KEY = "master_link"
JSON_HIS_VID_LINKS_KEY = "vid_links"

#VERSION
try:
	from version import __version__
except ImportError:
	from .version import __version__

import sys
import platform
import pip
import os.path
import string
try:
	#python2
	from Queue import Queue
except ImportError:
	#python3
	from queue import Queue

import re
import threading
import time
import shutil
import json

from datetime import timedelta

import requests
from lxml import html

try:
	#python2
	from urlparse import urlparse
except ImportError:
	#python3
	from urllib.parse import urlparse

try:
        from session_make import makeSession
except ImportError:
        from .session_make import makeSession

try:
	from openloaddecode import openload_decode
except ImportError:
	from .openloaddecode import openload_decode

try:
	from js_exc_decode import jsdecode
except ImportError:
	from .js_exc_decode import jsdecode

try:
	from kissenc import kissencCartoon, kissencAsian, kissencAnime
except ImportError:
	from .kissenc import kissencCartoon, kissencAsian, kissencAnime

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
        
#GOTTA GET THAT VERSION
#Get python version
PYTHON_VER = sys.version_info[0]

def autoUpdate():
	printClr("Checking for updates", Color.BOLD)
	pip.main(['install', '-U', '--no-cache-dir', '--no-deps', 'kissanime_dl'])

def printCapchaWarning():
        printClr("Warning: KissCartoon and KissAsian tend to ask for capcha after 5 video intervals.", Color.BOLD, Color.YELLOW)
        
NAME = 0
DOWNLOAD_URL = 1
PARENT_URL = 2

console_mu = threading.Lock()
write_hist = threading.Lock()

def writeHistory(urls_arr, PATH_TO_HISTORY, masterurl):
	#lets write that history file!
	link_history_data = {}

	#open that file
	#reads file no matter what
	if(os.path.isfile(PATH_TO_HISTORY) == True):
		with open(PATH_TO_HISTORY) as f:
			link_history_data = json.load(f)

	json_his_data = {JSON_HIS_MASTER_LINK_KEY:masterurl}

	#not update
	if(len(link_history_data) == 0):
		json_his_data[JSON_HIS_VID_LINKS_KEY] = urls_arr
	else:
		#is update
		temp_data = link_history_data[JSON_HIS_VID_LINKS_KEY]
		for lnk in urls_arr:
			temp_data.append(lnk)

		json_his_data[JSON_HIS_VID_LINKS_KEY] = temp_data
	with open(PATH_TO_HISTORY, 'w') as f_data:
		json.dump(json_his_data, f_data)

#cross version
def cVunicode(any):
	try:
		return unicode(any, utf8)
	except NameError:
		return str(any)

def downloadFile(url, dl_path, PATH_TO_HISTORY, masterurl):
	dl_name = cVunicode(url[NAME])
	dl_path = cVunicode(dl_path)

	if(type(dl_name) != type(str() ) ):
                #incase any strange happenings happen with extracting the filename
                dl_name = url[DOWNLOAD_URL]
	
	if(len(dl_name) > 252):
		dl_name = dl_name[:252]

	f_name = dl_path + "/" + dl_name + ".mp4"
	size = 0

	if(os.path.isfile(f_name) ):
		size = os.path.getsize(f_name)
		console_mu.acquire()
		print("Resuming download of " + dl_name)
		console_mu.release()
	else:
		console_mu.acquire()
		print("Beginning to download " + dl_name)
		console_mu.release()


	#Range Header prepare
	#For resuming downloads
	range_header = {'Range': 'bytes=%d-' % size}
	data = requests.get(url[DOWNLOAD_URL], headers=range_header, stream = True)


	type_of_file_op = ''

	#Check to see if partial content status code is sent back
	if(data.status_code == 206):
		type_of_file_op = "ab"
	else:
		type_of_file_op = "wb"

	with open(f_name, type_of_file_op) as dl_file:
		shutil.copyfileobj(data.raw, dl_file)
	del data

	#write to data immediately to save
	write_hist.acquire()
	writeHistory([url[PARENT_URL] ], PATH_TO_HISTORY, masterurl)
	write_hist.release()

	console_mu.acquire()
	print("Finished downloading " + dl_name)
	console_mu.release()

def decodeAA(text):
	return openload_decode(text)

def decodeFunky(text):
	return jsdecode(text)

def printError():
	printClr("The first argument is the url or update", Color.BOLD)
	print("    'update' can only be given if kissanime_dl has been run in that directory before")
	print("    The url can be from kissanime.to, kisscartoon.me, and kissasian.com")
	printClr("The second argument is the path to download to", Color.BOLD)
	printClr("An optional argument is --verbose", Color.BOLD)
	printClr("An optional argument is --simulate.", Color.BOLD)
	print("    This simulates finding the links, but doesn't download")
	printClr("An optional argument is --episode=OPT_BEG%OPT_END.", Color.BOLD)
	print("    If only OPT_BEG is given WITHOUT '%', only one episode will be downloaded.")
	print("    If only OPT_BEG is given WITH '%', then all files after OPT_BEG will be downloaded.")
	print("    If only OPT_END is given WITH '%', then all files before OPT_END will be downloaded.")
	print("    If OPT_BEG and OPT_END is given, then a range between the two will be downloaded.")
	print("    '%'' literal needs to be between the two.")
	print("    OPT_BEG needs to be above OPT_END in terms of the page (usually from largest to smallest)")
	print("    Defaults to all")
	printClr("An optional argument is --max_threads=VAL.", Color.BOLD)
	print("    Val is the number of threads to SEARCH for the download links")
	print("    Defaults to 5")
	print("    Downloading the files uses one thread per file and CANNOT be changed")
	printClr("An optional argument is --quality=QUAL", Color.BOLD)
	print("    This sets the quality of the video download")
	printClr("An optional argument is --txtlinks", Color.BOLD)
	print("    This creates a txt file with the links to the videos, but does not download them")
	printClr("An optional argument is --forcehistory", Color.BOLD)
	print("    Forces a history to be written with the given episodes.")
	print("    This is good for manually setting files you don't want to download when updating")
	printClr("An optional argument is --openload", Color.BOLD)
	print("    Forces to download from openload and attempts blogspot if openload is not supported on the page.")
	printClr("An optional argument is --noupdate", Color.BOLD)
	print("    Prevents the program from checking for and updating to the newest version of kissanime_dl")
	printClr("An optional argument is --delay=SEC", Color.BOLD)
	print("    Sets the delay in seconds between requests to the url given in the first argument.")
	printClr("An optional argument is --help", Color.BOLD)

def getElapsedTime(s_time):
	end_time = time.time()
	return str(timedelta(seconds = (end_time - s_time) ) )

# MAIN
def main():
	#required for py2js
	sys.setrecursionlimit(6000)

	LINK_HISTORY_FILE_NAME = "kissanime_dl_history.json"
	"""
	Json data should look like this:
	[
	"master_link" : MASTER_LINK,
	"vid_links" : [VID_LINKS]
	]

	"""

	#beginning clock
	start_time = time.time()
	plat = platform.system()
	print("Platform: " + plat)
	print("Python Version: " + str(PYTHON_VER) )
	printClr("Program Version: " + __version__, Color.BOLD)

	verbose = False
	simulate = False
	txtlinks = False
	forcehistory = False
	openload = False
	auto_update = True

	episode_range = []
	episode_range_single = False

	MAX_THREADS = 5
	quality_txt = ""

	sleepy_time = 0.1

	#optional args
	if(len(sys.argv) > 3):
		for i in range (3, len(sys.argv) ):
			psd_arg = sys.argv[i]
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
					episode_range_single = True
					first = eps
					second = "000"
					while(len(first) < 3):
						first = "0" + first
				else:

					eps = eps.split('%')
					if(len(eps) == 1):
						first = eps[0]
						if(first == ''):
							printClr("Error: The arguments cannot be blank", Color.BOLD, Color.RED)
							printError()
							return

						while(len(first) < 3):
							first = "0" + first
						second = "000"

					elif(len(eps) == 2):
						first = eps[0]
						while(len(first) < 3):
							first = "0" + first
						second = eps[1]
						while(len(second) < 3):
							second = "0" + second

						if(first == "000" and second == "000"):
							printClr("Error: Both arguments cannot be blank", Color.BOLD, Color.RED)
							printError()
							return

				EPS_PREFIX = "Episode-"
				if(EPS_PREFIX not in first and len(first) == 3):
					first = EPS_PREFIX + first
				if(EPS_PREFIX not in second and len(second) == 3 and len(eps) == 2):
					second = EPS_PREFIX + second

				episode_range = [first, second]

				if(verbose and not episode_range_single):
					print("Searching for episodes between: " + episode_range[0] + " and " + episode_range[1])
				elif(verbose and episode_range_single):
					print("Searching for episode: " + episode_range[0])

			elif(case_arg == "--max_threads"):
				str_val = psd_arg.split('=')[1]
				if(not str_val.isdigit() ):
					printClr("Error: " + str_val + " is not a valid value for threading", Color.BOLD, Color.RED)
					return

				MAX_THREADS = int(psd_arg.split('=')[1])

				if(MAX_THREADS < 1):
					printClr("Error: Cannot have max threads less than 1", Color.BOLD, Color.RED)
					return

			elif(case_arg == "--quality"):
				quality_txt = psd_arg.split('=')[1]
				if(not quality_txt.isdigit() and quality_txt[:-1] is not 'p'):
					printClr("Error: " + quality_txt + " is not a numerical value", Color.BOLD, Color.RED)
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

			else:
				printClr("Unknown argument: " + sys.argv[i], Color.BOLD, Color.RED)
				printError()
				return

	if(len(sys.argv) == 1):
		printError()
		return

	if(len(sys.argv) < 3):
		printClr("Error: kissanime_dl takes in 2 args, the url, and the path to download to", Color.BOLD, Color.RED)
		printError()
		return

	#check for updates
	if auto_update:
		autoUpdate()

	#print that capcha warning
	printCapchaWarning()


	#gets first arg
	url = sys.argv[1]

	dl_path = os.path.abspath(sys.argv[2])

	PATH_TO_HISTORY = dl_path + "/" + LINK_HISTORY_FILE_NAME

	if(os.path.isdir(dl_path) == False):
		printClr(dl_path + " is not a valid directory", Color.BOLD, Color.RED)
		printError()
		return

	if(url == "update"):
		#grab the urls
		#if update is passed in

		#check if update file exists
		if(not os.path.isfile(PATH_TO_HISTORY) ):
			printClr("Cannot update videos when kissanime_dl has never been run at " + dl_path, Color.BOLD, Color.RED)
			printClr("Make sure that " + LINK_HISTORY_FILE_NAME + " exists at that directory", Color.BOLD)
			return

	magiclink = {}

	#load update file if it exists to prevent redownloading
	if(os.path.isfile(PATH_TO_HISTORY) == True):
		with open(PATH_TO_HISTORY) as f:
			magiclink = json.load(f)

	if(url == "update"):
		url = magiclink[JSON_HIS_MASTER_LINK_KEY]
		if(verbose):
			print("Found url from history: " + url)

		if(url != magiclink[JSON_HIS_MASTER_LINK_KEY] ):
			#check to make sure that what is being passed in is in a new directory or the same url
			printClr("The url passed in does not match the url(" + magiclink[JSON_HIS_MASTER_LINK_KEY] + ")present in " + LINK_HISTORY_FILE_NAME, Color.BOLD, Color.RED)
			printClr("Try running kissanime_dl in another directory", Color.BOLD)
			return

	#Makes sure to connect to valid-ish urls.
	vurl_result = [i for i in valid_begin if i in url]
	vurl_result += [i for i in valid_end if i in url]
	vurl_result[0] = "http://" + vurl_result[0]

	if(url != "update"):

		if(len(vurl_result) < 2):
			printClr(url + " is not a valid url!", Color.BOLD, Color.RED)
			return


		#Makes sure okay connection to site
		thehead = requests.head(url)
		if(thehead.status_code != requests.codes.ok and thehead.status_code != 503):
			printClr("Failed to get a good status code at " + url, Color.BOLD, Color.RED)
			printClr("Status Code: " + str(thehead.status_code), Color.BOLD, Color.RED)
			return

	#new session creater
	sess = makeSession(url, vurl_result, verbose)
	r = sess.get(url, timeout=30.0)

	URL_ERROR_URL = vurl_result[-1] + "/Error"
	if(r.url == URL_ERROR_URL):
		printClr("Url error at " + url, Color.BOLD, Color.RED)
		print("Check your url and try again")
		return

	if(r.status_code != requests.codes.ok):
		printClr("Error: HTTP RESPONSE CODE: " + str(r.status_code), Color.BOLD, Color.RED)
		return

	printClr("Success!", Color.BOLD, Color.GREEN)

	#ASSUMING PAGE IS LOADED STARTING HERE

	tree = html.fromstring(r.content)

	LINK_TABLE_X_PATH = "//table[@class='listing']/tr/td/a"
	vid_lxml_ele = tree.xpath(LINK_TABLE_X_PATH)

	js_var_t_href = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))

	vid_links = []
	for i in range(len(vid_lxml_ele) ):
		vid_links.append(js_var_t_href[:-1] + vid_lxml_ele[i].attrib['href'])
		if(verbose):
			print("Found link: " + js_var_t_href[:-1] + vid_lxml_ele[i].attrib['href'])

	mu = threading.Lock()
	print_mu = threading.Lock()

	DOWNLOAD_URL_X_PATH = "//select[@id='selectQuality']"
	DOWNLOAD_URL_X_PATH_DEFAULT = DOWNLOAD_URL_X_PATH + "/option[1]/@value"
	DOWNLOAD_NAME = "//div[@id='divFileName']/b/following::node()"
	if(quality_txt != ""):
		DOWNLOAD_URL_X_PATH = DOWNLOAD_URL_X_PATH + "/option[normalize-space(text() ) = \'" + quality_txt + "\']/@value"
	else:
		#defaults to highest quality
		DOWNLOAD_URL_X_PATH = DOWNLOAD_URL_X_PATH_DEFAULT

	#arr of all the escape chars
	escapes = ''.join([chr(char) for char in range(1, 32)])

	if(verbose):
		print("Vidlinks: ")
		print(vid_links)

	if(len(episode_range) > 0):
		EPISODE_NULL_TITLE = "Episode-000"

		#checks to make sure episode entered is real
		fst_ln_fnd = False;
		snd_ln_fnd = False;
		for ln in vid_links:
			frmt_ln = ln.split("/")[-1].split("?")[0]
			if(episode_range[0] in frmt_ln):
				fst_ln_fnd = True
			if(episode_range[1] in frmt_ln):
				snd_ln_fnd = True
			if(fst_ln_fnd and snd_ln_fnd):
				break;

		if(not fst_ln_fnd and episode_range[0] != EPISODE_NULL_TITLE):
			printClr(episode_range[0] + " is not a valid episode", Color.BOLD, Color.RED)
			return

		if(not snd_ln_fnd and episode_range[1] != EPISODE_NULL_TITLE and not episode_range_single):
			printClr(episode_range[1] + " is not a valid episode", Color.BOLD, Color.RED)
			return

		rm_links = []

		if verbose:
			print("Removing episodes")

		if(episode_range[0] != EPISODE_NULL_TITLE and episode_range_single == False):
			for ln in vid_links:
				frmt_ln = ln.split("/")[-1].split("?")[0]
				if(episode_range[0] not in frmt_ln):
					rm_links.append(ln)
				else:
					break

		if(episode_range[1] != EPISODE_NULL_TITLE and episode_range_single == False):
			for ln in reversed(vid_links):
				frmt_ln = ln.split("/")[-1].split("?")[0]
				if(episode_range[1] not in frmt_ln):
					rm_links.append(ln)
				else:
					break

		if(episode_range_single == True):
			for ln in vid_links:
				if(episode_range[0] not in ln):
					rm_links.append(ln)

		for ln in rm_links:
			if(verbose):
				print("Removing link: " + ln)
			if ln in vid_links:
				vid_links.remove(ln)


	#assumes first arg is update
	#checks to see if link_history_data has data in it
	if(len(magiclink) != 0):
		for lnk in magiclink[JSON_HIS_VID_LINKS_KEY]:
			if(lnk in vid_links):
				if(verbose):
					print("Removing link: " + lnk)
				#removes link if file is in update
				vid_links.remove(lnk)

	if(len(vid_links) == 0):
		if(len(magiclink) != 0):
			printClr("No video updates found!", Color.BOLD, Color.RED)
			return

		printClr("No video links are found!", Color.BOLD, Color.RED)
		return

	if(len(vid_links) < MAX_THREADS):
		MAX_THREADS = len(vid_links)

	global dl_url_x_path
	dl_url_x_path = DOWNLOAD_URL_X_PATH

	def getOpenLoadUrls(queuee, link, ses, sleeptime):

		time.sleep(sleeptime)

		payload = {"s" : "openload"}

		mu.acquire()
		html_raw = ses.get(link, params=payload)
		mu.release()

		html_str = html_raw.content

		lxml_parse = html.fromstring(html_str)

		#Selected server option
		SEL_SER_OPT = "//select[@id='selectServer']/option[text()='Openload']"
		if(len(lxml_parse.xpath(SEL_SER_OPT) ) == 0):
			return False;

		find_str = r"""src=\"https?:\/\/openload.co(.*?)\""""

		try:
			raw_data = re.search(find_str, html_str).group(1)
		except AttributeError as e:
			printClr("Regex Failure", Color.RED, Color.BOLD)
			printClr("Could not find '" + find_str + "'", Color.RED, Color.BOLD)
			return False;
		except TypeError:
			raw_data = re.search(find_str, html_str.decode(html_raw.encoding) ).group(1)
		except:
			printClr("Unknown Regex Error", Color.RED, Color.BOLD)
			printClr("Pattern: " + find_str, Color.RED, Color.BOLD)
			return False;

		raw_data = "http://openload.co" + raw_data
		raw_data = raw_data.replace("embed", "f")

		mu.acquire()
		temp_r = ses.get(raw_data)
		mu.release()

		try:
			aaencoded = re.search(">ﾟωﾟﾉ= (.*?) \('_'\);", temp_r.content).group(1)
		except AttributeError as e:
			printClr("Regex Failure", Color.RED, Color.BOLD)
			printClr("Could not find '>ﾟωﾟﾉ= (.*?) \('_'\);' in " + raw_data, Color.RED, Color.BOLD)
			return False;
		except TypeError:
			aaencoded = re.search(">ﾟωﾟﾉ= (.*?) \('_'\);", temp_r.text).group(1)
		except:
			printClr("Unknown Regex Error", Color.RED, Color.BOLD)
			printClr("Pattern: >ﾟωﾟﾉ= (.*?) \('_'\);", Color.RED, Color.BOLD)
			return False;

		#need to add beginning and ending face to complete the encoded string
		aaencoded = "ﾟωﾟﾉ= " + aaencoded + " ('_');"

		decodedaa = decodeAA(aaencoded)

		try:
			decodedaa = re.search("function\(\)(.*)\(\)", decodedaa).group(1)
		except AttributeError as e:
			printClr("Regex Failure", Color.RED, Color.BOLD)
			printClr("Could not find 'function\(\)(.*)\(\)' in " + decodedaa, Color.RED, Color.BOLD)
			return False;
		except:
			printClr("Unknown Regex Error", Color.RED, Color.BOLD)
			printClr("Pattern: function\(\)(.*)\(\)", Color.RED, Color.BOLD)
			return False;

		#need to add function call and anonymous function
		decodedaa = "function()" + decodedaa + "();"

		#sometimes there are double +?
		decodedaa = decodedaa.replace("++", "+")

		try:
			decodedaa = re.search(".*(return)(.*)}", decodedaa).group(2)
		except AttributeError as e:
			printClr("Regex Failure", Color.RED, Color.BOLD)
			printClr("Could not find '.*(return)(.*)}' in " + decodedaa, Color.RED, Color.BOLD)
			return False;
		except:
			printClr("Unknown Regex Error", Color.RED, Color.BOLD)
			printClr("Pattern: .*(return)(.*)}", Color.RED, Color.BOLD)
			return False;

		decodedaa = decodedaa.replace(" ", '')
		decodedaa = decodedaa.replace("\n", '')

		deobfuscatedaa = decodeFunky(decodedaa)

		mu.acquire()
		temp_head = requests.head(deobfuscatedaa)
		mu.release()

		#openload now redirects
		redirect = temp_head.headers['location']

		"""
		for old version of code

		mu.acquire()
		temp_head = requests.head(deobfuscatedaa)
		mu.release()


		d = temp_head.headers['content-disposition']
		file_name = re.findall("filename=(.+)", d)[0]
		file_name = file_name.replace("\"", '')
		file_name = file_name.replace(" ", '')
		file_name = file_name.replace(".mp4", '')
		"""
		try:
			file_name = re.search("([^/]*)\?", redirect).group(1)
			file_name = file_name.replace(".mp4", '')
		except Exception:
			file_name = re.search("[^/]+$", link)

		queuee.put([file_name, redirect, link])

		if(verbose):
			print_mu.acquire()
			print("Found download link: " + redirect)
			print("Found file name: " + file_name)
			print_mu.release()

	def getBlogspotUrls(queuee, link, ses, sleeptime):
		time.sleep(sleeptime)

		#lets make a copy
		global dl_url_x_path

		payload = {"s" : "kissanime"}

		mu.acquire()
		html_raw = ses.get(link, params=payload)
		mu.release()

		html_str = html_raw.content

		temp_tree = html.fromstring(html_str)
		raw_data = temp_tree.xpath(DOWNLOAD_NAME)

		if(len(raw_data) == 0):
			return False

		def sanitize(funky_str):
			#removes all those escape chars from the string
			try:
				ft = funky_str.replace(" ", '').translate(None, escapes)
			except TypeError:
				try:
					ft = funky_str.replace(" ", '').translate(str.maketrans(dict.fromkeys(escapes) ) )
				except AttributeError:
					#python 2
					ft = funky_str.replace(" ", '').translate(dict.fromkeys(escapes) )

			return ft

		format_txt = sanitize(raw_data[0])

		#With email protection, sometimes only the [ is shown
		if(format_txt == "["):
			#hmm. this is a hacky fix
			#The rest of the data is generally in 5?
			format_txt = format_txt + sanitize(raw_data[5])

			#no quality found
		if(len(temp_tree.xpath(dl_url_x_path) ) == 0 and quality_txt != ""):
			printClr("Quality " + quality_txt + " is not found", Color.RED, Color.BOLD)
			printClr("Defaulting to highest quality", Color.BOLD)
			dl_url_x_path = DOWNLOAD_URL_X_PATH_DEFAULT

		discovered_url = ""

		if("/Anime/" in link):
			#site is kissanime
			discovered_url = kissencAnime(temp_tree.xpath(dl_url_x_path)[0])
		elif("/Cartoon/" in link):
			#site is kisscartoon
			discovered_url = kissencCartoon(temp_tree.xpath(dl_url_x_path)[0], ses)
		elif("/Drama/" in link):
			#site is kissasian
			discovered_url = kissencAsian(temp_tree.xpath(dl_url_x_path)[0], ses)
		else:
			#unknown site
			printClr("Error in finding method to decode video url from " + link, Color.RED, Color.BOLD)
			return False

		queuee.put([format_txt, discovered_url, link])
		if(verbose):
			print_mu.acquire()
			print("Found download link: " + discovered_url)
			print("Found file name: " + format_txt)
			print_mu.release()


	def getDLUrls(queuee, links, ses, sleepy_time, sleepy_increment):
		try:
			count = 0
			for ur in links:
				if(openload == False):
					if(getBlogspotUrls(queuee, ur, ses, sleepy_increment * count + sleepy_time) == False):
						if(getOpenLoadUrls(queuee, ur, ses, sleepy_increment * count + sleepy_time) == False):
							printClr("Failed to find url. You may have to check capcha, or KissAnime may have changed video host.", Color.RED, Color.BOLD)
				elif(openload == True):
					if(getOpenLoadUrls(queuee, ur, ses, sleepy_increment * count + sleepy_time) == False):
						if(getBlogspotUrls(queuee, ur, ses, sleepy_increment * count + sleepy_time) == False):
							printClr("Failed to find url. You may have to check capcha, or KissAnime may have changed video host.", Color.RED, Color.BOLD)
				count += 1
		except:
			return

	CHUNK_SIZE = int(round(len(vid_links) / float(MAX_THREADS) ) )
	dl_urls = Queue()
	thrs = []
	for i in range(MAX_THREADS):
		if(verbose):
			print("Creating Thread " + str(i) )
		loc_data = []
		if(i == MAX_THREADS - 1):
			loc_data = vid_links[(i * CHUNK_SIZE) : ]
		else:
			loc_data = vid_links[(i * CHUNK_SIZE) : (i * CHUNK_SIZE + CHUNK_SIZE)]
		if(verbose):
			print((i * CHUNK_SIZE))
			print((i * CHUNK_SIZE + CHUNK_SIZE))
			print(loc_data)
		thrs.append(threading.Thread(target = getDLUrls, args = (dl_urls, loc_data, sess, sleepy_time * i + sleepy_time, sleepy_time * MAX_THREADS) ) )
		thrs[i].daemon = True
		thrs[i].start()

	while(threading.active_count() > 1):
		#wait one tenth of a sec
		time.sleep(0.1)

	del thrs

	#lets clean up
	del tree
	del vid_lxml_ele
	del r
	del vid_links

	dl_urls = [item for item in dl_urls.queue]

	if(simulate):
		print("Finished simulation")
		if(forcehistory):
			writeHistory([lnk[PARENT_URL] for lnk in dl_urls], PATH_TO_HISTORY, url)

		printClr("Found " + str(len(dl_urls) ) + " links", Color.BOLD, Color.GREEN)
		printClr("Elapsed time: " + getElapsedTime(start_time), Color.BOLD)
		return

	if(txtlinks):
		print("Finished grabbing download links")
		FILE_NAME = "Links.txt"
		FILE_PATH = dl_path + "/" + FILE_NAME

		if(forcehistory):
			writeHistory([lnk[PARENT_URL] for lnk in dl_urls], PATH_TO_HISTORY, url)

		with open(FILE_PATH, 'w') as txt_data:
			for item in dl_urls:
				txt_data.write(item[DOWNLOAD_URL] + "\n")

		printClr("Found " + str(len(dl_urls) ) + " links", Color.BOLD, Color.GREEN)
		printClr("Elapsed time: " + getElapsedTime(start_time), Color.BOLD)
		return

	thrs = []

	#more threads to start downloading
	lazy_programming = 0
	for dl_sing_url in dl_urls:
		thrs.append(threading.Thread(target = downloadFile, args = (dl_sing_url, dl_path, PATH_TO_HISTORY, url) ) )
		thrs[lazy_programming].daemon = True
		thrs[lazy_programming].start()
		lazy_programming += 1

	while(threading.active_count() > 1):
		#wait one tenth of a sec
		time.sleep(0.1)

	printClr("Downloaded " + str(len(dl_urls) ) + " files at " + dl_path, Color.BOLD, Color.GREEN)
	printClr("Elapsed time: " + getElapsedTime(start_time), Color.BOLD)
