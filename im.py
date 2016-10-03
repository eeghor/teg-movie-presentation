"""
The IMDB 5000 Movie Database pre-processing. Additional data scraped from imdb.com.
---
usage: python3 im.py [data file]
"""

import pandas as pd  
import sys  		 
import re  			 # search for something in a string
from string import printable  # remove unprintable characters
import requests  	 # html scraping
from bs4 import BeautifulSoup  # HTML parsing
import time

first_relevant_year = 1991  # only consider movies released since this year

fl = sys.argv[1]  # movie database file; assume that fl has the form [name].[extension]
fl_upd = fl.split(".")[0]+"_upd.csv" # file to store processed data 

start_time = time.time()

df = pd.read_csv(fl, encoding="utf-8", dtype={"title_year": float})

print("found {} records (movies) in the database file".format(len(df.index)))

df = df[df["title_year"] >= first_relevant_year]
ndf = len(df.index)
print("removed movies released prior to {}; now have {} movies left".format(first_relevant_year, ndf))

# noticed unprintable characters - remove these
df["movie_title"] = df["movie_title"].apply(lambda _: "".join([ch for ch in _ if ch in printable]).lower().strip())

# to extract release date
rd = re.compile(r"(\d\d?\s+\w+\s+\d{4})")

# lists to collect new data in
rd_list  = [None]*ndf  # release dates
tg_list  = [None]*ndf  # taglines


for g, link in enumerate(df["movie_imdb_link"],1):

	print("processing page {} out of {}..".format(g, ndf))

	r = requests.get(link)
	soup = BeautifulSoup(r.content,"lxml")  # create soup object

	for line in soup.find_all('h4'):
		if line.text == "Release Date:":
			try:
				rd_list[g-1] = re.search(rd,line.next_sibling.strip()).group(0)
			except:
				pass
		elif line.text == "Taglines:":
				tg_list[g-1] = line.next_sibling.strip()

df["rel_date"] = rd_list
df["tagline"] = tg_list

df.to_csv(fl_upd)

end_time = time.time()

print("done. saved data to {}; elapsed time is {} minutes".format(fl_upd, round((end_time - start_time)/60,1)))
