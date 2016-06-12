#kissanime-dl

[![Build Status](https://travis-ci.org/wileyyugioh/kissanime_dl.svg?branch=master)](https://travis-ci.org/wileyyugioh/kissanime_dl)


Downloads all mp4s from a kissanime, kisscartoon, or kissasian mastersite!
(kissanime.to/Anime/*, kisscartoon.me/Cartoon/*, kissasian.com/Drama/)

##Currently supports as hosts:

Blogspot

Openload.co


##DOES NOT SUPPORT ONEDRIVE


#Dependencies:
lxml

requests

js2py

pycryptodome

#Installation
##*nix or OSX:

For some odd reason, this requires sudo for lxml 3.6.0
```
STATIC_DEPS=true sudo -H pip install lxml==3.6.0
pip install kissanime_dl
```

Alternative installation instructions for Linux if facing problems with  `pip`
```
# Remove problematic pip install
sudo apt-get remove python-pip

# Install dependencies
sudo apt-get install python-setuptools libxslt1-dev python-dev zlib1g-dev build-essential libgmp3c2 pypy-dev
sudo easy_install pip
sudo pip install --upgrade requests
sudo pip install js2py
sudo pip install cryptodome
sudo easy_install lxml==3.6.0

# Install kissanime_dl
pip install -U kissanime_dl
```

Note :  If  `pip install -U kissanime_dl`  is run with root privileges,
        the module throws errors if update is available. This happens
        as the module is unable to write to its install directory to
        perform the update. The solution to this is to either not
        install module with root privileges or run download as root
        once an update is available and normally after that

##Windows:

Windows is a tricky one.

Try:
```
pip install kissanime_dl
```

If you get an error like:
```
error: Microsoft Visual C++ 10.0 is required (Unable to find vcvarsall.bat)
```

There are more steps needed. First, go to

http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml

and download the proper 3.6.0 lxml wheel.

Then, type
```
pip install PATH_LXML
```
where PATH_LXML is the path to the lxml wheel you downloaded.

Then, try to reinstall.

#Usage:
```

Type into shell:
kissanime-dl URL PATH_TO_DOWNLOAD OPT_ARGS

####
MAKE SURE THAT kissanime_dl RUNS IN SEPARATE DIRECTORIES FOR DIFFERENT URLS, OR ELSE UPDATE WILL BE SCREWY
####

First argument: the url to the kiss-site master page. It can also be "update" which will download any videos not downloaded into the folder.
"update" can only be used if kissanime_dl has been run in that directory and has generated a history file

Second argument: the path to download files to

Optional arguments:

--verbose: Verbose output

--simulate: Grabs download urls, but doesn't download

--episode=OPT_BEG%OPT_END: Downloads specific episodes.
	If only OPT_BEG is given WITHOUT "%", only one episode will be downloaded.
	If only OPT_BEG is given WITH "%", then all files after OPT_BEG will be downloaded.
	If only OPT_END is given WITH "%", then all files before OPT_END will be downloaded.
	If OPT_BEG and OPT_END is given, then a range between the two will be downloaded.
	"%" literal needs to be between the two.
	OPT_BEG needs to be above OPT_END in terms of the page

--max_threads=VAL: Sets the max_threads to search for the download urls.
	The threads for the actual downloading is not affected.
	The actual downloading uses one thread per file

--quality=QUAL: Sets the quality of the downloaded video.
	If the quality is not found, the highest one is downloaded

--txtlinks
	Doesn't downloads the videos, but prints the direct video urls into a txt file.

--forcehistory
	Forces a history to be written with the given episodes.
	This is good for manually setting files you don't want to download when updating

—-openload
	Puts priority to using openload as host.

—noupdate
	Prevents kissanime_dl from autoupdating

--delay=SEC
    Adds a delay between get requests to the master page
    Value in seconds

--help: Prints help
```


#Example Usage
```

##Initial run
kissanime-dl https://kissanime.to/Anime/NHK-ni-Youkoso ~/Videos/NHK

##To update videos
kissanime-dl update ~/Videos/NHK

##Download one episode
kissanime-dl https://kissanime.to/Anime/NHK-ni-Youkoso ~/Videos/NHK --episode=5

##Download range of episodes
kissanime-dl https://kissanime.to/Anime/NHK-ni-Youkoso ~/Videos/NHK --episode=20%4

##Choose quality
kissanime-dl https://kissanime.to/Anime/NHK-ni-Youkoso ~/Videos/NHK --quality=1080

##Make txt file
kissanime-dl https://kissanime.to/Anime/NHK-ni-Youkoso ~/Videos/NHK --txtlinks

##Force history
kissanime-dl https://kissanime.to/Anime/NHK-ni-Youkoso ~/Videos/NHK --forcehistory
```
I think you get the picture
