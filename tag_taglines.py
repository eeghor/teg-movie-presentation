import spacy
import sys
import pandas as pd


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
		print("looks like tagline is empty!")
		r = None
	return r

for i, tg in enumerate(df["tagline"].astype(str)):

	if len(tg) > 0:
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

df.to_csv(fl_upd)