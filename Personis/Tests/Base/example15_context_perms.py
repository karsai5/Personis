#!/usr/bin/env python

import Personis_base
from Personis_util import showobj, printcomplist
from Crypto.PublicKey import RSA
from Personis_exceptions import AuthRequestedError

def printAskContext( info ):
	(cobjlist, contexts, theviews, thesubs) = info
	printcomplist(cobjlist, printev = "yes")
	print "Contexts: %s" % str(contexts)
	print "Views: %s" % str(theviews)
	print "Subscriptions: %s" % str(thesubs)
		
print "==================================================================="
print "Examples that show how app registration works"
print "==================================================================="

um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='user', auth='alice:secret')

print "List the registered apps (should be none):"
apps = um.listapps()
print apps

print "Try and set permissions on a context for an unregistered app:"
try:
	um.setpermission(context=["Personal"], app="MyHealth", permissions={'ask':True, 'tell':False})
except Exception as e:
	print "setpermission failed with exception : %s\n" % (e)

print "Register an app"
try:
    key = Personis_base.generate_app_key("MyHealth")
    fingerprint = Personis_base.generate_app_fingerprint(key)
    Personis_base.AppRequestAuth(model='Alice', modeldir='Tests/Models', app='MyHealth', key=key.publickey().exportKey(), description="My Health Manager")
except Exception as e:
    print "App auth request failed with exception : %s\n" % (e)

requests = um.listrequests()
print requests
fingerprint2 = requests['MyHealth']['fingerprint']
if fingerprint2 != fingerprint:
	print "Fingerprints don't match!"
else:
	print "Fingerprints match"
appdetails = um.registerapp(app="MyHealth", desc="My Health Manager", fingerprint=fingerprint)
print "Registered ok: ", appdetails
print "List the registered apps (should be one):"
apps = um.listapps()
print apps

print "Set some permissions for the 'MyHealth' app"
um.setpermission(context=["Personal"], app="MyHealth", permissions={'ask':False, 'tell':False, "resolvers":["last1", "goal"]})

print "Show the permissions:"
perms = um.getpermission(context=["Personal"], app="MyHealth")
print "MyHealth:", perms

print "Try getting permissions for an unregistered app:"
try:
	perms = um.getpermission(context=["Personal"], app="withings")
except Exception as e:
	print "Access failed with exception : %s\n" % (e)
else:
	print "withings:", perms

print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++"
print "Now testing permissions"
print
print "Tell full name as owner"
ev = Personis_base.Evidence(evidence_type="explicit", value="Alice")
um.tell(context=["Personal"], componentid='firstname', evidence=ev)
ev = Personis_base.Evidence(evidence_type="explicit", value="Smith")
um.tell(context=["Personal"], componentid='lastname', evidence=ev)

print "Ask for Alice's fullname as owner (should work)"
reslist = um.ask(context=["Personal"], view='fullname')
print reslist[0].value, reslist[1].value

um = None
print "Access Alice's model as an unregistered App:"
try:
	unregistered_key = Personis_base.generate_app_key("MyHealth")
	auth = 'withings:' + Personis_base.generate_app_signature('withings', unregistered_key)
	um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='app', auth=auth)
except Exception as e:
	print "Access failed with exception : %s\n" % (e)

um = None
print "Access Alice's model as a registered App (should work):"
try:
	auth = 'MyHealth:' + Personis_base.generate_app_signature('MyHealth', key) 
	um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='app', auth=auth)
except Exception as e:
	print "Access failed with exception : %s\n" % (e)

print "Ask for Alice's fullname as app 'MyHealth' (should NOT work)"
try:
	reslist = um.ask(context=["Personal"], view='fullname')
	print reslist[0].value, reslist[1].value
except Exception as e:
	print "ask failed with exception : %s\n" % (e)

print "Set ask permission for the 'MyHealth' app"
um = None
um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='user', auth='alice:secret')
um.setpermission(context=["Personal"], app="MyHealth", permissions={'ask':True, 'tell':False})


um = None
auth = 'MyHealth:' + Personis_base.generate_app_signature('MyHealth', key) 
um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='app', auth=auth)
print "Ask for Alice's fullname as app 'MyHealth' (should work now)"
try:
	reslist = um.ask(context=["Personal"], view='fullname')
	print reslist[0].value, reslist[1].value
except Exception as e:
	print "ask failed with exception : %s\n" % (e)

print "Now try and tell a new value for first name (should NOT work)"
ev = Personis_base.Evidence(evidence_type="explicit", value="Fred")
try:
	um.tell(context=["Personal"], componentid='firstname', evidence=ev)
except Exception as e:
	print "tell failed with exception : %s\n" % (e)

print "Delete the 'MyHealth' app while NOT accessing as owner"
try:
	um.deleteapp(app="MyHealth")
except Exception as e:
	print "deletapp failed with exception : %s\n" % (e)
else:
	print "FAILED: deleteapp should not be able to delete app when not owner"

um = None
um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='user', auth='alice:secret')
print "Delete the 'MyHealth' app while accessing as owner"
try:
	um.deleteapp(app="MyHealth")
except Exception as e:
	print "deleteapp failed with exception : %s\n" % (e)
else:
	print "deleteapp succeeded"
print "List the registered apps (should be none):"
apps = um.listapps()
print apps
