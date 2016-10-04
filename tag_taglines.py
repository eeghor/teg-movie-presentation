import spacy
import sys
import pandas as pd
from collections import Counter
import math
from string import printable  # remove unprintable characters


en_nlp = spacy.load('en')

fl = sys.argv[1]  # movie database file; assume that fl has the form [name].[extension]
fl_upd = fl.split(".")[0]+"_w_pos.csv" # file to store processed data 

df = pd.read_csv(fl)

print(df.head())

pct_verbs = [None]*len(df["tagline"])
pct_punkt = [None]*len(df["tagline"])
pct_nouns = [None]*len(df["tagline"])
pct_adj = [None]*len(df["tagline"])

print("lists are ", len(pct_verbs))

def calcPercent(num,denom):
	try:
		r = round(100*num/denom,1)
	except ZeroDivisionError:
		print("looks like your tagline is empty!")
		r = None
	return r

for i, tg in enumerate(df["tagline"].astype(str)):

	if len(tg) > 0 and tg != "nan" :

		doc = en_nlp(tg)
		pos_this_tagline = [token.pos_ for token in doc]

		# count all POS
		nPOS = len(pos_this_tagline)
		# count % verb
		pct_verbs[i] = calcPercent(pos_this_tagline.count("VERB"),nPOS)
		pct_punkt[i] = calcPercent(pos_this_tagline.count("PUNCT"),nPOS)
		pct_nouns[i] = calcPercent(pos_this_tagline.count("NOUN"),nPOS)
		pct_adj[i] = calcPercent(pos_this_tagline.count("ADJ"),nPOS)

df["tagline_pct_verbs"] = pct_verbs
df["tagline_pct_punkt"] = pct_punkt
df["tagline_pct_nouns"] = pct_nouns
df["tagline_pct_adj"] = pct_adj

# action and fantasy content in %
# tmp_series = df["genres"].apply(lambda _: Counter([x.strip() for  x in _.split("|")]))
df["pct_action_fantasy"] = df["genres"].apply(lambda _: Counter([x.strip() for  x in _.split("|")])).apply(lambda _: round(100*(_["Action"]+_["Fantasy"])/sum(_.values()),1))

# add plot complexity
df["plot_complexity"] = df["plot_keywords"].astype(str).apply(lambda _: len([y  for w in [x.strip().split() for x in _.split("|")] for y in w ]))


df["rel_date"] = pd.to_datetime(df["rel_date"],infer_datetime_format=True)
df["rel_weekday"] = df["rel_date"].dt.weekday  # Monday=0, Sunday=6
df["rel_quarter"] = df["rel_date"].dt.quarter  # Jan=Mar = 1, Apr-Jun = 2, etc.

male_names = []
female_names = []

with open("data/person_female.txt","r") as f:
    for line in f:
        female_names.append(line.strip())
print("got a list of {} female names".format(len(female_names)))

with open("data/person_male.txt","r") as f:
    for line in f:
        male_names.append(line.strip())
print("got a list of {} male names".format(len(male_names)))

"""
create a list of M/F for a series of names
"""
def getSexList(ser):
    _f_name = ser.astype(str).apply(lambda _: _.strip().split()[0])
    _male_idx = _f_name.isin(male_names)
    _female_idx = _f_name.isin(female_names)
    return ["F" if i else "M" for i in _female_idx]

df["director_sex"] = getSexList(df["director_name"])
df["actor_1_sex"] = getSexList(df["actor_1_name"])
df["actor_2_sex"] = getSexList(df["actor_2_name"])
df["actor_3_sex"] = getSexList(df["actor_3_name"])



df.to_csv(fl_upd)