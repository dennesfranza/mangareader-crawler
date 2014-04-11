#! /usr/bin/python

import os, re, sys, subprocess
from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError, HTTPError

homepage = "http://www.mangareader.net"

def main():

	weblink = os.path.join(homepage, sys.argv[1])
	soup = BeautifulSoup(urlopen(weblink))
	xfind = soup.find(id="listing")

	def sanitize(obj):
		return re.sub(r'/', '.', obj)

	for links in xfind.find_all('a'):
		ref = links.get('href')
		nlink = homepage + ref
		fname = sanitize(ref)
		if fname:
			if not os.path.exists(fname):
				os.mkdir(fname)
				os.chdir(fname)
				soup2 = BeautifulSoup(urlopen(nlink))
				find = soup2.find_all('option')
				for xlink in find:
					xget = xlink.get('value')
					llink = homepage + xget
					if llink:
						soup3 = BeautifulSoup(urlopen(llink))
						_find = soup3.find('img')
						_get = _find.get('src')
						subprocess.call(['wget', '-nc', _get])
				os.chdir(os.path.dirname(os.getcwd()))

if __name__ == '__main__':
	main()
