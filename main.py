from tkinter import Tk
from tkinter import filedialog
from os import listdir,walk,path
from os.path import isfile, join
import sys
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
from operator import itemgetter
import time



root = Tk()
root.withdraw()

print("Choose the directory from which you want to choose movies:")
time.sleep(4)


mypath = filedialog.askdirectory()
if(len(mypath) < 1):
	print("Not a valid directory!")
	sys.exit(1)
print(mypath)

files = []
for (dirpath, dirnames, filenames) in walk(mypath):
    files.extend(filenames)
possible_formats = [".webm", ".mkv", ".flv", ".vob", ".avi", ".mov", ".wmv", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".3gp"]

#making lists of movies
movies = []
for file in files:
	for extension in possible_formats:
		if(file.endswith(extension)):
			movies.append(file)

data = [[] for i in range(len(movies))]
print(len(movies))
#data = dict()
#modifying names removing irrelevant parts like [1080p] or anything within square brackets
modified_movies = []
for movie in movies:
	movie = path.splitext(movie)[0]
	remove = re.search('\\[.*\\]',movie)
	if remove is not None:
		remove = remove.group()
		modified_movies.append(movie.replace(remove, ""))
	else:
		modified_movies.append(movie)

'''
	Removing some more strings is necessary may be
	BluRay,m1080p , m720p, (E-Subs) ,720p.x264,720p, 1080p, 1080p.x264, x265, x264, 10bit, 6CH, HEVC-PSA,YIFY, WEB-DL, English,   
	or 
	some common user of torrent from whom you download your files
	many possiblities
'''

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = 'https://www.imdb.com'
QUERY = '/find?q='
# appending this to BASE_URL + QUERY + MOVIE_NAME gives only movies in search results
ONLY_MOVIES = '&s=tt&ttype=ft&ref_=fn_ft'
counter=0;
for movie in modified_movies:
	url = BASE_URL + QUERY + '+'.join(movie.split()) + ONLY_MOVIES
	html = urlopen(url, context=ctx).read()
	soup = BeautifulSoup(html, "html.parser")
	tags = soup.find('tr', {"class", "findResult odd"})
	#for link in tags.select("a"):
	#	print(link['href'])
	if tags is None:
		print("this ", movie, "has some  problem")
	else:
		#print(tags.select("a")[0]["href"])
		htm = urlopen( BASE_URL+tags.select("a")[0]["href"], context=ctx).read()
		s = BeautifulSoup(htm, "html.parser")
		# to get movie name, ratings, genre, storyline
		ratings = s.find('span', {"class", "rating"})
		#print(ratings)	
		extracted_rating = re.findall("\d\.\d", str(ratings))
		#print(temp)
		genre_list = []
		genres = s.findAll("span", {"itemprop" : "genre"})
		for genre in genres:
			genre_list.append(genre.text)
		storylines = s.findAll("span", {"itemprop" : "description"})
		try:
			data[counter] = [movie, float(extracted_rating[0]), genre_list, storylines[0].text, url] # user can find more info about particular info at url
		except:
			print(movie,"this is creating a prob", counter , "is count")
		counter = counter + 1
new_data = sorted(data, key=itemgetter(1),reverse=1)

fhand = open('index.html', 'w')
# change this html to something better than this 
for x in new_data:
	fhand.write("<h3>" + x[0] + " Rating: "+ str(x[1]) +"</h3>")

fhand.close()
