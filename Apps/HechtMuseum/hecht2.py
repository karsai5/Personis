#!/usr/bin/env python

import sys
import Personis
import Personis_base
from Personis_util import showobj, printcomplist

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
# prog run when a presentation is played, stopped or rated

if len(sys.argv) != 5:
	print "usage: %s user password presentation meta" % (sys.argv[0])
	print "example: %s bob pass1 p204 play" % (sys.argv[0])
	sys.exit(1)

user = sys.argv[1]
password = sys.argv[2]
presentation = sys.argv[3]
meta = sys.argv[4]

mum = Personis.Access(model="HechtMuseum@s1.personis.info:2001", user='bob', password="pass1")
uum = Personis.Access(model=user+"@s1.personis.info:2001", user=user, password=password) 

print ">>> tell %s %s -> /%s/Apps/HechtMuseum/presentation" % (presentation, meta, user)
ev = Personis_base.Evidence(evidence_type="explicit", value="%s %s"%(presentation,meta))
print uum.tell(context=["Apps","HechtMuseum"], componentid='presentation', evidence=ev)

print ">>> ask /HechtMuseum/Presentations/%s -> metadata + question" % (presentation)
reslist = mum.ask(context=["Presentations"], view=[presentation], resolver={'evidence_filter':"all"})
metalist = [x.value for x in reslist[0].evidencelist]
print presentation, "\t", metalist
for meta_item in metalist:
	t,m = meta_item.split(" ", 1)
	if t == "meta":
		print ">>> tell %s %s -> /%s/Apps/HechtMuseum/metadata" % (m, meta, user)
		ev = Personis_base.Evidence(evidence_type="explicit", value="%s %s"%(m,meta))
		print uum.tell(context=["Apps","HechtMuseum"], componentid='metadata', evidence=ev)


