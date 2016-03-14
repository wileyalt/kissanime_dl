#kissanime-dl


Downloads all mp4s from a kissanime mastersite!
(kissanime.to/Anime/*)

##Currently supports as hosts:

Blogspot

Openload.co


##DOES NOT SUPPORT ONEDRIVE


#Dependencies:
lxml

requests

js2py


#Installation
##*nix or OSX:

```
STATIC_DEPS=true sudo pip install lxml
```

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

and download the proper lxml wheel.

Then, type
```
pip install PATH_LXML
```
where PATH_LXML is the path to the lxml wheel you downloaded.

Then, try to reinstall.

**FOR ALL WINDOWS INSTALLATIONS**

**BUT WAIT, THERE'S MORE**

Due to a bug in pip, the script it generates is broken, and needs to be manually fixed.

Type in 
```
pip show kissanime-dl
```

and go up the filesystem to the pythonXX\Scripts directory, where there should be a file named
```
kissanime-dl-script.py
```
open it in a text editor and change
```
#!LONG, LONG, PATH
```
to 
```
#!"LONG, LONG, PATH"
```
This is because spaces in the path name screw everything up, and that bug in pip still hasn't been fixed.

Everything should be installed properly, and this can be verified by typing into cmd:
```
kissanime-dl
```


#Usage:
```

Type into shell:
kissanime-dl URL PATH_TO_DOWNLOAD OPT_ARGS

####
MAKE SURE THAT kissanime_dl RUNS IN SEPARATE DIRECTORIES FOR DIFFERENT URLS, OR ELSE UPDATE WILL BE SCREWY
####

First argument: the url to the kissanime.to/Anime/* page. It can also be "update" which will download any videos not downloaded into the folder. 
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
