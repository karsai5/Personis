#!/usr/local/bin/python

import sys
import Personis
import Personis_base
from Personis_util import showobj, printcomplist

um = Personis.Access(model="bob", user='bob')

if len(sys.argv) == 2:
	contextstring = sys.argv[1]
else:
	contextstring = "/"

contextpath = contextstring.split("/")
if contextpath[0] == '':
	contextpath = contextpath[1:]

res = um.ask(context=contextpath, showcontexts=True)

print "Category", contextstring
print "\tComponents of this category"
for c in res[0]:
	print "\t\t", c.Identifier, "("+c.Description+")"
print "\tSub-Categories"
for c in res[1]:
	print "\t\t", c

