import pandas as pd 
import sys
import re
from collections import defaultdict
from string import printable
import requests
from bs4 import BeautifulSoup
import json

# y1 = 1996

# # release-dates.list from ftp://ftp.fu-berlin.de/pub/misc/movies/database/
# # The Innkeepers (2011)					USA:29 September 2011	(Fantastic Fest)

# df = pd.DataFrame(columns=["title","year","r_country","r_date"])

# mvs = re.compile(r"\"(?P<title>.*?)\"\s+\((?P<year>199[6-9]+|2\d{2}6)\)\s+(?P<country>\w+):(?P<r_date>.*\d{4})")
# #mvs2 = re.compile(r"\"(?P<title>.*?)\"\s+\((?P<year>201[4-5]{1})\)\s+(?P<genre>\w+)")

# fl = sys.argv[1]
# #fl2 = sys.argv[2]

# c = 0

# print("searching for movies reeased since {} in the release date database...".format(y1))

# with open(fl,"r",encoding='utf-8', errors='ignore') as f:
# 	for line in f:
# 		m = re.search(mvs,line)  # . Matches any single character except newline; $ Matches end of line; ? Matches 0 or 1 occurrence of preceding expression
# 		if m:
# 			df.loc[c] = [m.group("title"),m.group("year"),m.group("country"),m.group("r_date")]
# 			c += 1

# df["title"] = df["title"].str.lower().str.strip()
# #df["title"] = df["title"].apply(lambda _: _.strip())

# print("collected {} movies ({}-{})".format(len(df.index),df["year"].min(),df["year"].max()))
# print(df["title"][:20])

df1 = pd.read_csv("movie_metadata.csv",encoding="utf-8")
# #print(df1["movie_title"][:5])
#df1["movie_title"] = df1["movie_title"].str.lower().str.strip()
df1["movie_title"] = df1["movie_title"].apply(lambda _: "".join([ch for ch in _ if ch in printable]).lower().strip())
# print("so now we have..")
# print(df1["movie_title"][:10])

#print("found {} in both dataframes".format(len(set(df1["movie_title"]).intersection(set(df["title"])))))
#print(df["title"])
# for m in df["title"]:
# 	if df1["movie_title"].isin(m):
# 		print("found movie",m)

# to extract release date
rd = re.compile(r"(\d\d?\s+\w+\s+\d{4})")

# for release dates
rd_dict  = defaultdict(list)
tg_dict  = defaultdict(list)

# extract links
for link in df1["movie_imdb_link"]:
	r = requests.get(link)
	soup = BeautifulSoup(r.content,"lxml")
	for line in soup.find_all('h4'):
		if line.text == "Release Date:":
			try:
				m = re.search(rd,line.next_sibling.strip())
				rd_dict["rel_date"].append(m)
			except TypeError:
				rd_dict["rel_date"].append(None)
		elif line.text == "Taglines:":
				tag = line.next_sibling.strip()
				if len(tag) > 0:
					tg_dict["tagline"].append(line.next_sibling.strip())
				else:
					tg_dict["tagline"].append(None)

print("found {} release dates".format(len(rd_dict)))
print("found {} taglines".format(len(tg_dict)))

df1.append(rd_dict)
df1.append(tg_dict)

with open("movie_df.json","w") as f:
	json.dump(df1,f)

#	tree = ET.fromstring(r.content)
	#tree = ET.parse(r)
	#root = tree.getroot()
	#print(root)

