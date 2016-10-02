import pandas as pd  # to use data frames
import sys  # for command line argument(s)
import re  # search for something
from string import printable  # remove unprintable characters
import requests  # html scraping
from bs4 import BeautifulSoup  # scraping
import time

# mvs = re.compile(r"\"(?P<title>.*?)\"\s+\((?P<year>199[6-9]+|2\d{2}6)\)\s+(?P<country>\w+):(?P<r_date>.*\d{4})")
# #mvs2 = re.compile(r"\"(?P<title>.*?)\"\s+\((?P<year>201[4-5]{1})\)\s+(?P<genre>\w+)")

fl = sys.argv[1]  # movie database file
fl_upd = fl.split(".").insert("_upd.",1)  # file to store processed data

start_time = time.time()
df = pd.read_csv(fl, encoding="utf-8")
ndf = len(df.index)
print("found {} records (movies) in the database file")

# noticed unprintable characters - remove these
df["movie_title"] = df["movie_title"].apply(lambda _: "".join([ch for ch in _ if ch in printable]).lower().strip())

# to extract release date
rd = re.compile(r"(\d\d?\s+\w+\s+\d{4})")

# lists to collect.. 
rd_list  = []  # release dates
tg_list  = []  # taglines


for g, link in enumerate(df["movie_imdb_link"],1):

	print("processing page {} out of {}..".format(g, ndf))

	r = requests.get(link)
	soup = BeautifulSoup(r.content,"lxml")  # create soup object

	for line in soup.find_all('h4'):
		if line.text == "Release Date:":
			try:
				rd_list.append(re.search(rd,line.next_sibling.strip()))
			except TypeError:
				rd_list.append(None)
		elif line.text == "Taglines:":
				tagl = line.next_sibling.strip()
				if len(tagl) > 0:
					tg_list.append(tagl)
				else:
					tg_list.append(None)

print("found {} release dates and {} taglines".format(len(rd_list), len(tg_list)))

df["rel_date"] = rd_list
df["tagline"] = tg_list

df.to_csv(fl_upd)

end_time = time.time()

print("done. elapsed time is {} minutes".format(round((end_time - start_time)/60,1)))
