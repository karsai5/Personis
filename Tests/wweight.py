#!/usr/bin/env python

import Personis
import Personis_base
from urllib2 import urlopen
import json, time

u = urlopen("http://wbsapi.withings.net/measure?action=getmeas&userid=14044&publickey=a724d144737439b5&limit=1")
res = u.read()
res = json.jsonToObj(res)

mtime = res['body']['measuregrps'][0]['date']
weight = res['body']['measuregrps'][0]['measures'][0]['value']/1000.0

print "Time:", time.ctime(mtime), "Weight:", weight

um = Personis.Access(model="bob", user='bob')
ev = Personis_base.Evidence(source="withings", evidence_type="given", value=weight, time=mtime)
um.tell(context=["Personal", "Health"], componentid='weight', evidence=ev)
