"""
Scrape potentially useful additional data from www.imdb.com and add it to the IMDB 5000 Movie Database 
from www.kaggle.com (downloaded as a .csv file)
---
usage: python3 get_additional_data.py [data file]
---
igor k. 05-oct-2016
"""

import pandas as pd  
import sys  		 
import re 	# need to search within a string
from string import printable  # remove unprintable characters
import requests 	# to grab HTML
from bs4 import BeautifulSoup  # HTML parsing
import time

# movie database file name; assumed to be of the form [name].[extension]
fl = sys.argv[1]  
# file to store the dataset with additional data (yes, we keep the original)
fl_upd = fl.split(".")[0]+"_upd.csv"  

# only consider movies released since this year (incl.):
FRY = 1991  # "First Relevant Year"

start_time = time.time()

df = pd.read_csv(fl, encoding="utf-8", dtype={"title_year": float})
print("found {} records (movies) in the database file".format(len(df.index)))

# SOME DATA ADJUSTMENT

# discard all movies released before FRY
df = df[df["title_year"] >= FRY]
ndf = len(df.index)
print("removed movies released prior to {}; now have {} movies left".format(FRY, ndf))
# note: unprintable characters occur in movie titles! remove these
df["movie_title"] = df["movie_title"].apply(lambda _: "".join([ch for ch in _ if ch in printable]).lower().strip())

# SCRAPING

# to extract release date; see the IMDB movie page source
rd = re.compile(r"(\d\d?\s+\w+\s+\d{4})")

# lists to collect new data in
rd_list  = [None]*ndf  # release dates
tg_list  = [None]*ndf  # taglines

# recall that df["movie_imdb_link"] contains all links to movie pages
for g, link in enumerate(df["movie_imdb_link"],1):

	print("processing page {} out of {}..".format(g, ndf))

	r = requests.get(link)
	soup = BeautifulSoup(r.content,"lxml")  # create soup object

	for line in soup.find_all('h4'): # why: see the IMDB movie page source
		if line.text == "Release Date:":
			try:
				rd_list[g-1] = re.search(rd,line.next_sibling.strip()).group(0)
			except:
				pass
		elif line.text == "Taglines:":
				tg_list[g-1] = line.next_sibling.strip()

# add new columns to data frame
df["rel_date"] = rd_list
df["tagline"] = tg_list

# dump data frame to .csv
df.to_csv(fl_upd)

end_time = time.time()
print("done. saved data to {}; elapsed time: {} minutes".format(fl_upd, round((end_time - start_time)/60,1)))
