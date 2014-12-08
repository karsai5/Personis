#!/usr/bin/env python

import sys
import Personis
import Personis_base
from Personis_util import showobj, printcomplist

Debug = False
#######
#
# model structure:
# 
# /HechtMuseum/
# 	Locations/
# 		placename	presentation
# 		eg Menorah		p204
# 	Presentations/
# 		presentation	place | metadata | question
# 		eg p204		Menorah
# 		eg p204		people
# 		eg p204		"Blah blah?"
# 
# /User/Apps/HechMuseum/
# 	location	placename
# 			eg Menorah
# 	user-id		museumUserCode
# 	presentation	presentation played | presentation stopped | presentation rating
# 			eg p204 played
# 			eg p204 rating 2
# 	metadata	metaname rating
# 			eg people 2
# 	
#######

# prog run when user is detected at new location.
# find available presentations and rank them for this user

def resolve(reslist):
	pres_ratings = [x.value for x in reslist[0].evidencelist]
	ratings = {}
	raw = {}
	for r in pres_ratings:
		pres,rate = r.split(" ",1)
		if pres in raw:
			raw[pres].append(rate)
		else:
			raw[pres] = [rate]
	
	for pres in raw:
		ratings[pres] = 0
		for r in raw[pres]:
			if r == "play":
				ratings[pres] += 1
			elif r == "stop":
				ratings[pres] -=1
			else:
				ratings[pres] += int(r.split(1)[1])
	return ratings

if len(sys.argv) != 4:
	print "usage: %s user password placename" % (sys.argv[0])
	print "example: %s bob pass1 MenorahJewishEpigraphy" % (sys.argv[0])
	sys.exit(1)

user = sys.argv[1]
password = sys.argv[2]
placename = sys.argv[3]

mum = Personis.Access(model="HechtMuseum@s1.personis.info:2001", user='bob', password="pass1")
uum = Personis.Access(model=user+"@s1.personis.info:2001", user=user, password=password) 

if Debug: print ">>> ask /HechtMuseum/Locations/placename -> presentations"
reslist = mum.ask(context=["Locations"], view=[placename], resolver={'evidence_filter':"all"})
evlist = reslist[0].evidencelist
presentations = [x.value for x in evlist]
if Debug: print presentations
#printcomplist(reslist, printev = "yes")

# ask /User/Apps/HechtMuseum/presentations -> pres ratings
if Debug: print ">>> ask /%s/Apps/HechtMuseum/presentations -> presentation ratings" % (user)
reslist = uum.ask(context=["Apps", "HechtMuseum"], view=["presentation"], resolver={'evidence_filter':"all"})
ratings = resolve(reslist)
if Debug: print ratings

# ask /User/Apps/HechtMuseum/metadata -> metaname ratings
if Debug: print ">>> ask /%s/Apps/HechtMuseum/metadata -> metaname ratings" % (user)
reslist = uum.ask(context=["Apps", "HechtMuseum"], view=["metadata"], resolver={'evidence_filter':"all"})
meta_ratings = resolve(reslist)
if Debug: print meta_ratings

def cmp(p1,p2):
	if p1[1] < p2[1]:
		return 1
	elif p1[1] > p2[1]:
		return -1
	else:
		return 0

presrate = []
presmeta = {}
for presentation in presentations:
	if Debug: print ">>>\t", presentation
	if not (presentation in ratings):
		ratings[presentation] = 0
	presrate.append((presentation, ratings[presentation]))
	if Debug: print ">>> ask /HechtMuseum/Presentations/pres -> metadata + question"
	reslist = mum.ask(context=["Presentations"], view=[presentation], resolver={'evidence_filter':"all"})
	metalist = [x.value for x in reslist[0].evidencelist]
	metadict = {}
	for x in metalist:
		t,v = x.split(" ",1)
		if t == "meta":
			if t in metadict:
				metadict[t].append(v)
			else:
				metadict[t] = [v]
		else:
			metadict[t] = v
	presmeta[presentation] = metadict

presrate.sort(cmp)

print "You are at location '%s'." % (placename)
print "Select a presentation:"
for p,r in presrate:
	metadict = presmeta[p]
	print "\t", metadict["question"], metadict["meta"]
	
	

