#!/usr/bin/env python

"""
Personis_mkmodel - library functions used to create sets of models.
	Used by the program mkmodel

mkmodel takes a definition of a model (stored in modeldefinitionfile)
and creates a model in modeldirectory for each model 


"""

import sys
import Personis_base
import Personis_a
import Personis_server


"""
	Functions for parsing modeldefs. Uses the pyparsing module 

 Modeldef statement grammar:

	name := ID
	flag := '[' QUOTEDSTRING [',' QUOTEDSTRING]* ']'
	value := QUOTEDSTRING | flags
	key_value := name '=' value
	evidence := '[' key_value* ']'
	attribute := key_value | evidence
	path = [ '/' ] name [ '/' name ]*
	context := '@@' path ':' attribute [ ',' attribute ]*
	component := '--' name ':' attribute [ ',' attribute ]*
	view := '==' name ':' path [ ',' path ]

 Example:

@@Location: description="Information about the user's location."
--seenby: type="attribute", value_type="string", description="sensor that has seen this person"
--location: type="attribute", value_type="string", description="Location Component", 
	[evidence_type="explicit", value="Bob"], [evidence_type="explicit", flags= [ "f1", "f2" ], value="blah"]
==fullname: Personal/firstname, Personal/lastname

"""
from mypyparsing import Word, alphas, alphanums, Literal, ZeroOrMore, quotedString, Forward, removeQuotes, ParseException, Optional, OneOrMore

keyvals = {} # dictionary to hold list of key/value pairs for an element of the  modeldef
attrs = []
paths = [] # list of paths
flags = None
curcontext = ""
themodel = None
Debug = False


def doname(str, loc, toks):
#	print "doname::", toks
	pass

def doflaglist(str, loc, toks):
	global flags
#	print "doflaglist::", toks
	pass
	flags = []
	if (len(toks) < 3) or  (toks[0] != '[') or (toks[-1] != ']'):
		print "*** bad flag list: ", toks
		return
	for i in range(1,len(toks),2):
		flags.append(toks[i])
	print "\tflaglist:", flags

def dokeyval(str, loc, toks):
	global keyvals, flags
#	print "dokeyval::", toks
	if flags != None:
		val = flags
		flags = None
	else:
		val = toks[2]
	if toks[0] in keyvals:
		if type(keyvals[toks[0]]) == type([]):
			keyvals[toks[0]].append(val)
		else:
			keyvals[toks[0]] = [keyvals[toks[0]], val]
	else:
		keyvals[toks[0]] = val
#	print "\tkeyvals::", keyvals

def dokeyval_list(str, loc, toks):
	global keyvals, attrs
#	print "dokeyval_list::", toks
#	print "\tkeyvals", keyvals
	attrs.append(keyvals)
#	print " \tattrs::", attrs
	keyvals = {}


def doevidence(str, loc, toks):
	global attrs
#	print "doevidence:: ", toks
#	print "\t", attrs
	pass

def doevidencelist(str, loc, toks):
#	print "doevidencelist:: ", toks
	pass

def dotells(ev, compid):
	global themodel, curcontext
	evattrs = ["flags", "evidence_type", "source", "owner", "value", "comment", "time", "useby"]
	if not all([a in evattrs for a in ev]):
		print "**** evidence attributes %s must be one of %s" % (ev.keys(), `evattrs`)
		return 
	if "flags" in ev:
		if type(ev['flags']) != type([]):
			print "**** evidence flags %s must be a list" % (ev['flags'])
			return

	if not Debug:
		evobj = Personis_base.Evidence(evidence_type="explicit")
		for k,v in ev.items():
			evobj.__dict__[k] = v
		themodel.tell(context=curcontext, componentid=compid, evidence=evobj)
		print	"""
			evobj = Personis_base.Evidence(ev)
			themodel.tell(context=%s, componentid=%s, evidence=%s)
			""" % (curcontext, compid, evobj.__dict__)
	else:
		print	"""
			evobj = Personis_base.Evidence(ev)
			themodel.tell(context=%s, componentid=%s, evidence=%s)
			""" % (curcontext, compid, ev)
		
		


def docomponent(str, loc, toks):
	global attrs, keyvals, paths, curcontext, themodel, Debug
	if curcontext == "":
		print "No context defined for component", toks[1]
	print "docomponent::", toks[1]; sys.stdout.flush()
	print " \tattrs::", attrs
	required = ['type', 'description', 'value_type']
	for x in required:
		if x not in attrs[0]:
			print "one or more of the required keyvals", required, "not found for ", toks[1]
			print attrs[0]
			return
	if not Debug:
		cobj = Personis_base.Component(Identifier=toks[1],
			component_type=attrs[0]['type'],
			value_type=attrs[0]['value_type'],
			value_list=attrs[0].get('value'),
			resolver=attrs[0].get('resolver'),
			Description=attrs[0]['description'])
		try:
			res = themodel.mkcomponent(context=curcontext, componentobj=cobj)
		except:
			print "mkcomponent failed"
		if res != None:
			print res
	print """cobj = Personis_base.Component(Identifier="%s",
		component_type="%s",
		value_type="%s",
		value_list="%s",
		resolver="%s",
		Description="%s")
		""" % ( toks[1], attrs[0]['type'], attrs[0]['value_type'], attrs[0].get('value'), attrs[0].get('resolver'), attrs[0]['description'])
	if 'rule' in attrs[0]:
		if type(attrs[0]['rule']) != type([]):
			rules = [attrs[0]['rule']]
		for rule in rules:
			if not Debug:
				themodel.subscribe(context=curcontext, view=[toks[1]], subscription=dict(user="bob", password="qwert", statement=rule))
			print "\tsub::", curcontext, [toks[1]], dict(user="bob", password="qwert", statement=rule)
	print "+++ component created "
	if len(attrs) > 1: # see if there is some evidence
		for e in attrs[1:]:
			print "\tevidence::", e
			dotells(e, toks[1])
#	del attrs[0]
	attrs = []
	keyvals = {}
	paths = []

def docontext(str, loc, toks):
	global attrs, paths, curcontext, themodel, Debug, keyvals
	print "docontext::", toks
	print " \tpaths::", paths
	print " \tattrs::", attrs
	if len(paths) != 1:
		print "too many paths", paths
		raise ParseException, "too many paths " + `paths`
	curcontext = paths[0]
	print "\tcurcontext::", curcontext, curcontext.split('/')
	if 'description' not in attrs[0]:
		print "*** description required for ", curcontext
		raise ParseException, "description required for " + `curcontext`
	if not Debug:
		cobj = Personis_base.Context(Identifier=curcontext.split('/')[-1], Description=attrs[0]['description'])
	print "\tPersonis_base.Context(Identifier='%s', Description='%s')" % (curcontext.split('/')[-1], attrs[0]['description'])
	print "\t", curcontext.split('/')[:-1]
	if not Debug:
		if themodel.mkcontext(curcontext.split('/')[:-1], cobj):
			print "+++ context created ok"
		else:
			print "+++ context creation failed"
	keyvals = {}
	del attrs[0]
	paths = []

def domdef(str, loc, toks):
	#print "domdef::", toks
	print "--------------------------------"

def dopath(str, loc, toks):
	global paths
#	print "dopath::", toks
	paths.append(''.join(toks))

def doview(str, loc, toks):
	global paths, curcontext, themodel, Debug
	if curcontext == "":
		print "No context defined for view", toks[1]
		raise ParseException, "No context defined for view " + `toks[1]`
	if paths == []:
		print "No paths defined for view", toks[1]
		raise ParseException, "No paths defined for view " + `toks[1]`
	print "doview::", toks[1]
	print "\t paths::", paths
	if not Debug:
		vobj = Personis_base.View(Identifier=toks[1], component_list=paths)
		themodel.mkview(curcontext, vobj)
	paths = []

#	name := ID
#	attribute := name '=' QUOTEDSTRING
#	path = [ '/' ] name [ '/' name ]
#	context := path ':' attribute [ ',' attribute ]*
#	component := name ':' attribute [ ',' attribute ]*
#	view := name ':' path [ ',' path ]

name = Word(alphanums+"_")
flaglist = Literal('[')+ quotedString.setParseAction(removeQuotes) + ZeroOrMore(Literal(',') + quotedString.setParseAction(removeQuotes)) + Literal(']')
value = quotedString.setParseAction(removeQuotes) | flaglist
keyval = name + Literal("=") + value
keyval_list = keyval + ZeroOrMore(Literal(",") + keyval)
evidence = Literal("[") + keyval_list + Literal("]")
evidencelist = evidence + ZeroOrMore(Literal(",") + evidence)
path = ZeroOrMore(Literal('/')) + name + ZeroOrMore(Literal('/') + name)
context = Literal('@@') + path + Literal(':') + keyval_list
component = Literal('--') + name + Literal(":") + keyval_list + Optional(Literal(',') + evidencelist)
view = Literal('==') + name + Literal(":") + path + ZeroOrMore(Literal(",") + path)
mdef = OneOrMore(context + ZeroOrMore(component) + ZeroOrMore(view)) + Literal('$$')

name.setParseAction(doname)
keyval.setParseAction(dokeyval)
flaglist.setParseAction(doflaglist)
keyval_list.setParseAction(dokeyval_list)
evidence.setParseAction(doevidence)
evidencelist.setParseAction(doevidencelist)
path.setParseAction(dopath)
context.setParseAction(docontext)
component.setParseAction(docomponent)
view.setParseAction(doview)
mdef.setParseAction(domdef)


def domodeldef(mdefstring):
	"""
	function to parse a modeldef statement
	arg is a string containing the mdef statement
	"""
	mdefstring += " $$"
	#print "statement:", mdefstring
	try:
		toks = mdef.parseString(mdefstring)
	except ParseException, err:
		print '****  Parse Failure  ****'
		print err.line
		print " "*(err.column-1) + "^"
		print err

		raise ValueError, "parse failed"


"""====================================================================================================================="""
def mkmodel_um(um,lines, debug = 1):
	'''
		Create a model from the model definition in the string "lines"
	'''
	global themodel
	themodel = um
	domodeldef(lines)

def mkmodel_remote(model=None, mfile=None, modelserver=None, user=None, password=None):
	Personis_server.MkModel(model=model, modelserver=modelserver, user=user, password=password)
	auth = user + ":" + password
	um = Personis.Access(model=model, modelserver=modelserver, authType="user", auth=auth)
	mkmodel_um(um,get_modeldef(mfile))
	

def mkmodel(model=None, mfile=None, modeldir=None, user=None, password=None):
	Personis_base.MkModel(model=model, modeldir=modeldir, user=user, password=password)
	auth = user + ":" + password
	um = Personis_a.Access(model=model, modeldir=modeldir, authType="user", auth=auth)
	mkmodel_um(um,get_modeldef(mfile))

def get_modeldef(mfile):
	try:
		mf = open(mfile)
	except:
		print "cannot open <%s>" % (mfile)
		sys.exit(1)
	lines = ""
	for mline in mf.readlines():
#		mline = mline.strip()
#		if debug:
#			print ">"+mline
		if (len(mline) == 0) or (mline[0] in "#\n"):
			continue
		if mline[:9] == "$include ":
			inclfile = mline[9:].strip()
			print "#### include file: %s\n" % (inclfile)
			lines = lines + get_modeldef(inclfile)
			print "#### end of include file: %s\n" % (inclfile)
		else:
			lines = lines+mline
	mf.close()
	return lines


if __name__ == '__main__':
	Debug = True
	mdefstring = """
@@Location: description="Information about the user's location."
--seenby: type="attribute", value_type="string", description="sensor that has seen this person"
--location: type="attribute", value_type="string", description="Location Component", 
	[evidence_type="explicit", value="Bob"], [evidence_type="explicit", flags= [ "f1", "f2" ], value="blah"]
"""
	mmdefstring = """
@@Location: description="Information about the users' location."
--seenby: type="attribute", value_type="string", description="sensor that has seen this person"
--location: type="attribute", value_type="string", description="Location", [aa="hhh", bb="kk"]
==fullname: Personal/firstname, Personal/lastname
@@Personal/Work: description="Information about the users work."
--role: description="the users main role in the organisation", type="attribute",
        value_type="enum", value="Academic", value="Postgraduate", value="etc",
	rule="<default!./Personal/email> ~ '*' : NOTIFY 'http://www.somewhere.com/' 'email=' <./Personal/email>",
[aa="hhh", bb="jj"],
[aa="hhh", bb="kk"]
"""
	mmdefstring = """
@@Location: description="Information about the users' location."
--seenby: type="attribute", value_type="string", description="sensor that has seen this person"
--location: type="attribute", value_type="string", description="Location"
@@Work: description="Information about the users work."
--role: description="the users main role in the organisation", type="attribute", 
        value_type="enum", value="Academic", value="Postgraduate", value="etc"

"""
	mmdefstring = get_modeldef("Modeldefs/user-test")
	mdefstring = get_modeldef(sys.argv[1])
	print "=====================\n",mdefstring,"\n=====================\n"
#	domodeldef(mdefstring)

