#!/usr/bin/env python

import sys, os

sys.path.insert(0, '/home/bob/LLUM/PersonisLite/Src')
sys.path.insert(0, '/home/bob/LLUM/PersonisLite/lib/python')
sys.path.insert(0, '/home/bob/Python/lib/python')

import Personis
import Personis_base
from urllib2 import urlopen
import json, time

os.environ["http_proxy"] = "http://www-cache.cs.usyd.edu.au:8000/"

um = Personis.Access(model="bob", user='bob')
res = um.ask(context=["Personal","Health", "Medications"], view=['taken'], evidence_filter="all")
last_taken = res[0].evidencelist[0].time
lastt = time.localtime(last_taken)
tnow = time.localtime()

if (lastt.tm_hour == 20):
	if (tnow.tm_hour >= 7) and (tnow.tm_yday != lastt.tm_yday):
		result = ("OVERDUE", "last taken %s" % (time.ctime(last_taken)))
	else:
		result = ("OK","")
else:
	if (tnow.tm_hour >= 20):
		result = ("OVERDUE", "last taken %s" % (time.ctime(last_taken)))
	else:
		result = ("OK","")

import prowlpy

apikey = '520ac6714fce2b9b95cb3e111124ee7a5ba1f2eb' #API-key)
p = prowlpy.Prowl(apikey)
if result[0] == 'OVERDUE':
	try:
	    p.add('Pills','OVERDUE',result[1])
	    print 'Success'
	except Exception,msg:
	    print msg

#orbcolours = {'blue':24, 'green':9, 'yellow':6, 'red':0}
#orbpulserate = {'none':0, 'heartbeat':9, 'fast':6}
#orbbrightness = {'low':"0", 'medium':"1", 'high':"2"}
#orbdict = {'colour':orbcolours, 'pulse':orbpulserate, 'brightness':orbbrightness}
