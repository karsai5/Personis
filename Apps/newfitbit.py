#!/usr/bin/env python

import sys, os
import ConfigParser
from urllib2 import urlopen
import json, time
from  fitbit import Client
import datetime
#import pdb; pdb.set_trace()

# Personis Configuration
cfg = ConfigParser.ConfigParser()
cfg.read(os.path.expanduser("~/.personis.conf"))
personispath = cfg.get('paths', 'personis')
print "Path:", personispath
sys.path.insert(0, personispath)

import Personis
import Personis_base


def fitbit():
	res = um.ask(context=["Apps","Fitbit"], view=['steps'], resolver=dict(evidence_filter="all"))
	# Intraday time series
	steps = client.intraday_steps(yesterday)
	for ent in steps:
		#print ent['time'].ctime(), time.mktime(ent['time'].timetuple()),  ent['value']
		ftime = int(time.mktime(ent['time'].timetuple()))
		steps = int(ent['value'])
		#print 'FITBIT: steps=', steps, 'ftime=', ftime
		found = False
		for r in res:
			print "number of evidence items = ", len(r.evidencelist)
			for e in r.evidencelist:
				#print "EV:", e.value, e.time
				if ftime == int(e.time):
					if steps == int(e.value):
						found = True
						#print 'found'
						continue
		if not found:
			ev = Personis_base.Evidence(source='fitbit', evidence_type='explicit', time=ftime, value=steps)
			um.tell(context=["Apps","Fitbit"], componentid='steps', evidence=ev)
			print "Tell steps %d, %s" % (steps, ftime)


# Fitbit Configuration
CONFIG = ConfigParser.ConfigParser()
CONFIG.read(["fitbit.conf", os.path.expanduser("~/.fitbit.conf")])

client = Client(CONFIG.get('fitbit', 'user_id'),
                CONFIG.get('fitbit', 'sid'),
                CONFIG.get('fitbit', 'uid'),
                CONFIG.get('fitbit', 'uis'))

yesterday = datetime.date.today() - datetime.timedelta(days=1)

um = Personis.Access(model="bob@s1.personis.info:2001", user='bob', password='pass1')

fitbit()

