#kissanime_dl


Downloads all mp4s from a kissanime mastersite!
(kissanime.to/Anime/*)


#Dependencies:
lxml

requests


#Installation
```
pip install kissanime_dl
```


#Usage:
```
Type into shell:
kissanime-dl URL PATH_TO_DOWNLOAD OPT_ARGS

First argument: the url to the kissanime.to/Anime/* page.

Second argument: the path to download files to

Optional arguments:

--verbose: Verbose output

--simulate: Grabs download urls, but doesn't download

--episode=BEG%OPT_END: Downloads specific episodes. If only BEG is given, only one episode will be downloaded. If BEG and OPT_END is given, then a range between the two will be downloaded. "%" literal needs to be between the two. BEG needs to be above OPT_END in terms of the page

--max_threads=VAL: Sets the max_threads to search for the download urls. The threads for the actual downloading is not affected. The actual downloading uses one thread per file

--help: Prints help
```
