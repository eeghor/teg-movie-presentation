"""
Load the IBDM 5000 Movie database obtained from kaggle.com; it has already been extended to include 
taglines and full release dates. Now we generate some new variables and add the corresponding columns to the 
database.
---
usage: python3 generate_new_variables.py [data file]
---
igor k. 05-oct-2016
"""

import spacy  # need for POS tagging
import sys
import pandas as pd
from collections import Counter  # useful counter, for conveninence


fl = sys.argv[1]  # movie database file; assume that fl has the form [name].[extension]
fl_upd = fl.split(".")[0]+"_final.csv" # file to store processed data 

df = pd.read_csv(fl)
NVARS_WAS = df.shape[1]
# POS TAGGING

# load Spacy Engligh model
en_nlp = spacy.load('en')

# we are interested in percentage of verbs, nouns, punctuation marks
# and adjectives in the taglines; 

# function to calculate percentages; mainly to make code less repetitive
def calcPercent(num,denom):
	try:
		r = round(100*num/denom,1)
	except ZeroDivisionError:
		print("your tagline has length zero!")
		r = None
	return r

# create lists to store percentages
NTLS = len(df["tagline"])  # nuber of all taglines

pct_verbs = [None]*NTLS
pct_punkt = [None]*NTLS
pct_nouns = [None]*NTLS
pct_adj = [None]*NTLS

for i, tg in enumerate(df["tagline"].astype(str)):  # enforce string

	if len(tg) > 0 and tg != "nan":  # yes, there are "nan" as strings!

		doc = en_nlp(tg)  # create a "document"
		# collect all POS tags in a list
		pos_this_tagline = [token.pos_ for token in doc]
		NPOS = len(pos_this_tagline)

		# calculate %-s
		pct_verbs[i] = calcPercent(pos_this_tagline.count("VERB"),NPOS)
		pct_punkt[i] = calcPercent(pos_this_tagline.count("PUNCT"),NPOS)
		pct_nouns[i] = calcPercent(pos_this_tagline.count("NOUN"),NPOS)
		pct_adj[i] = calcPercent(pos_this_tagline.count("ADJ"),NPOS)

# add the corresponding columns to data frame
df["tagline_pct_verbs"] = pct_verbs
df["tagline_pct_punkt"] = pct_punkt
df["tagline_pct_nouns"] = pct_nouns
df["tagline_pct_adj"] = pct_adj

# CREATE ACTION AND FANTASY CONTENT VARIABLES

# the idea is that we want to have percentages of words "Action" and "Fantasy" in genre descriptions;
# why? based on "expert opinion" (client's priorities) that these two genres could be the key to 
# nice box office performance

df["pct_action_fantasy"] = df["genres"].apply(lambda _: Counter([x.strip() for x in _.split("|")])).apply(lambda _: 
																	round(100*(_["Action"]+_["Fantasy"])/sum(_.values()),1))

# CREATE PLOT COMPLEXITY VARIABLES

# there is a feeling that if a movies plot needs more words to describe, that is probably a sign of a more complex 
# story line

df["plot_complexity"] = df["plot_keywords"].astype(str).apply(lambda _: len([y for w in [x.strip().split()
																				for x in _.split("|")] for y in w ]))

# CREATE RELEASE DAY WEEKDAY AND QUARTER VARIABLES

# infer the datetime format first
df["rel_date"] = pd.to_datetime(df["rel_date"], infer_datetime_format=True)

df["rel_weekday"] = df["rel_date"].dt.weekday  # Monday=0, Sunday=6
df["rel_quarter"] = df["rel_date"].dt.quarter  # Jan=Mar = 1, Apr-Jun = 2, etc.

# FIGURE OUT DIRECTOR AND ACTOR GENDER AND ADD AS VARIABLES

male_names = []
female_names = []

# recall that we use GATE name gazetteers (downloaded)
with open("gazetteers/person_female.txt","r") as f:
    for line in f:
        female_names.append(line.strip())
print("got a list of {} female names".format(len(female_names)))

with open("gazetteers/person_male.txt","r") as f:
    for line in f:
        male_names.append(line.strip())
print("got a list of {} male names".format(len(male_names)))

# this function helps decide if a name is a male or female name
def getSexList(ser):
    _f_name = ser.astype(str).apply(lambda _: _.strip().split()[0])
    _male_idx = _f_name.isin(male_names)
    _female_idx = _f_name.isin(female_names)
    return ["F" if i else "M" for i in _female_idx]

# add the corresponding columns to data frame
df["director_sex"] = getSexList(df["director_name"])
df["actor_1_sex"] = getSexList(df["actor_1_name"])
df["actor_2_sex"] = getSexList(df["actor_2_name"])
df["actor_3_sex"] = getSexList(df["actor_3_name"])

NVARS_NOW = df.shape[1]  # how many variables now

# dump data frame to a new file (again, keep the original!)
df.to_csv(fl_upd, index=False)

print("done. saved database to {}. there are now {} variables (was {}).".format(fl_upd, NVARS_NOW, NVARS_WAS))