#!/usr/bin/env python

import Personis
import Personis_base
import time

um = Personis.Access(model="bob", user='bob')

reslist = um.ask(context=["Personal", "Health", "Medications"], view=['taken'], evidence_filter="all")

comp = reslist[0]
ev = comp.evidencelist[0]

day = 24*60*60
hour = 60*60

ttime = int(ev.time) % day
now = int(time.time()) % day

def time8(t):
	if (t > 8*hour) and (t < 20*hour):
		return 20*hour - t
	else:
		if t < 8*hour:
			return 8*hour - t
		else:
			return (24*hour - t) + 8*hour
		
def tstr(t):
	return str(t/60/60)+" hrs "+str((t%(60*60))/60)+" mins"

ttime = time8(ttime)
now = time8(now)
print "since taken",tstr(ttime)
print "from now",tstr(now)
print "difference",tstr(now - ttime)
