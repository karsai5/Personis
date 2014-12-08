#!/usr/bin/env python

#
# The Personis system is copyright 2000-2011 University of Sydney
#       Bob.Kummerfeld@Sydney.edu.au
# GPL v3
#
# Active User Models: added subscribe method to Access
#

import os, sys, httplib, traceback
import simplejson as json
import jsoncall
import cherrypy
import Personis_base
import Personis_a
import Personis_exceptions
import cPickle
import types
from Crypto.PublicKey import RSA

def MkModel( model=None, modelserver=None, user=None, password=None, description=None, debug=0, ca_certs_file="ca_certs/ca.pem"):
	if modelserver == None:
		raise ValueError, "modelserver is None"
	if ':' in modelserver:
		modelserver, modelport = modelserver.split(":")
	else:
		modelport = 2005 # default port for personis server
	modelname = model
	auth = user + ":" + password
	ok = False
	try:
		ok = jsoncall.do_call(modelserver, modelport, ca_certs_file, "mkmodel", {'modelname':modelname,\
									'descripion':description,\
									'authType':'user',\
									'auth':auth})
	except:
		if debug >0:
			traceback.print_exc()
		raise ValueError, "cannot create model '%s', server '%s'" % (modelname, modelserver)
	if not ok:
		raise ValueError, "server '%s' cannot create model '%s'" % (modelserver, modelname)

def AppRequestAuth(model=None, modelserver=None, app=None, key=None, description=None, debug=0, ca_certs_file="ca_certs/ca.pem"):
	if modelserver == None:
		raise ValueError, "modelserver is None"
	if ':' in modelserver:
		modelserver, modelport = modelserver.split(":")
	else:
		modelport = 2005 # default port for personis server
	modelname = model
	ok = False
	try:
		ok = jsoncall.do_call(modelserver, modelport, ca_certs_file, "apprequestauth", {'modelname':modelname,\
									'description':description,\
									'app':app,\
									'key':key})
	except:
		if debug >0:
			traceback.print_exc()
		raise ValueError, "cannot request authorisation for app '%s', server '%s'" % (app, modelserver)
	if not ok:
		raise ValueError, "server '%s' cannot process authorisation request for app '%s'" % (modelserver, app)

class Access(Personis_a.Access):
	""" 
	Client version of access for client/server system

	arguments:
		model		model name
		modelserver	model server and port
		user		user name
		password	password string
		app		app name
		description	app description
		ca_certs_file	file containing extra certificate authority certificates to use
	
	Either user and password, or app must be specified for successful authentication.

	returns a user model access object 
	"""
	def __init__(self, model=None, modelserver=None, user=None, password=None, app=None, description="", debug=0, ca_certs_file="ca_certs/ca.pem"):
		if modelserver == None:
			raise ValueError, "modelserver is None"
		if ':' in modelserver:
			self.modelserver, self.modelport = modelserver.split(":")
		else:
			self.modelserver = modelserver
			self.modelport = 2005 # default port for personis server
		self.modelname = model
		self.user = user
		self.password = password
		self.app = app
		self.description = description
		self.debug =debug
		self.key = None
		self.ca_certs_file = ca_certs_file
		if self.app == None:
			self.auth = user + ":" + password
			self.authType = "user"
		else:
			self.authType = "app"
			try:
				self.key = Personis_base.import_app_key(app)
			except Personis_exceptions.KeyFileNotFoundError:
				self.key = Personis_base.generate_app_key(self.app)
				fingerprint = Personis_base.generate_app_fingerprint(self.key)
				AppRequestAuth(model=self.modelname, modelserver=self.modelserver, app=self.app, 
					key=self.key.publickey().exportKey(), description=self.description)
				message = "Authorisation has been requested for app " + self.app + " to access model " + self.model + " on server " + self.modelserver + ".\n"
				message += "Key fingerprint: %s\n" % (fingerprint)
				raise Personis_exceptions.AuthRequestedError(message)

		ok = False
		try:
			command = "access"
			args = {'modelname':self.modelname}
			if self.app != None:
				self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
				args['authType'] = 'app'
			else:
				args['authType'] = 'user'
			args['auth'] = self.auth
			if self.debug != 0:
				print "jsondocall:", self.modelserver, self.modelport, self.ca_certs_file, self.modelname, self.authType, self.auth

			ok = jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, command, args)
			if self.debug != 0:
				print "---------------------- result returned", ok
		except:
			if debug >0:
				traceback.print_exc()
			raise
			raise ValueError, "cannot access model '%s', server '%s'" % (self.modelname, self.modelserver)
		if not ok:
			raise ValueError, "server '%s' cannot access model '%s'" % (self.modelserver, self.modelname)

	def ask(self,  
		context=[],
		view=None,
		resolver=None,
		showcontexts=None):
		"""
	arguments: (see Personis_base for details)
		context is a list giving the path of context identifiers
		view is either:
			an identifier of a view in the context specified
			a list of component identifiers or full path lists
			None indicating that the values of all components in
				the context be returned
		resolver specifies a resolver, default is the builtin resolver

	returns a list of component objects
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		reslist = jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "ask", {'modelname':self.modelname,\
												'authType':self.authType,\
												'auth':self.auth,\
												'context':context,\
												'view':view,\
												'resolver':resolver,\
												'showcontexts':showcontexts})
		complist = []
		if showcontexts:
			cobjlist, contexts, theviews, thesubs = reslist
			for c in cobjlist:
				comp = Personis_base.Component(**c)
				if c["evidencelist"]:
					comp.evidencelist = [Personis_base.Evidence(**e) for e in c["evidencelist"]]
				complist.append(comp)
			reslist = [complist, contexts, theviews, thesubs]
		else:
			for c in reslist:
				comp = Personis_base.Component(**c)
				if c["evidencelist"]:
					comp.evidencelist = [Personis_base.Evidence(**e) for e in c["evidencelist"]]
				complist.append(comp)
			reslist = complist
		return reslist
	
	def tell(self, 
		context=[],
		componentid=None,
		evidence=None):   # evidence obj
		"""
	arguments:
		context - a list giving the path to the required context
		componentid - identifier of the component
		evidence - evidence object to add to the component
		"""
		if componentid == None:
			raise ValueError, "tell: componentid is None"
		if evidence == None:
			raise ValueError, "tell: no evidence provided"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "tell", {'modelname':self.modelname,\
												'authType':self.authType,\
												'auth':self.auth,\
												'context':context,\
												'componentid':componentid,\
												'evidence':evidence.__dict__})
	def mkcomponent(self,
		context=[],
		componentobj=None):
                """
        Make a new component in a given context
        arguments:
                context - a list giving the path to the required context
                componentobj - a Component object
        returns:
                None on success
                a string error message on error
                """
		if componentobj == None:
			raise ValueError, "mkcomponent: componentobj is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "mkcomponent", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentobj':componentobj.__dict__})
	def delcomponent(self,
		context=[],
		componentid=None):
                """
        Delete an existing component in a given context
        arguments:
                context - a list giving the path to the required context
                id - the id for a componen
        returns:
                None on success
                a string error message on error
                """
		if componentid == None:
			raise ValueError, "delcomponent: componentid is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "delcomponent", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentid':componentid})
	def delcontext(self,
		context=[]):
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "delcontext", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context})
	def getresolvers(self):
		'''Return a list of the available resolver names'''
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "getresolvers", {'modelname':self.modelname,\
											'authType':self.authType, 'auth':self.auth})
	
	def setresolver(self,
		context,
		componentid,
		resolver):
                """
        set the resolver for a given component in a given context
        arguments:
                context - a list giving the path to the required context
		componentid - the id for a given component
                resolver - the id of the resolver
        returns:
                None on success
                a string error message on error
                """
		if componentid == None:
			raise ValueError, "setresolver: componentid is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "setresolver", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'componentid':componentid, \
											'resolver':resolver})
		
	def mkview(self,
		context=[],
		viewobj=None):
                """
        Make a new view in a given context
        arguments:
                context - a list giving the path to the required context
                viewobj - a View object
        returns:
                None on success
                a string error message on error
                """
		if viewobj == None:
			raise ValueError, "mkview: viewobj is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "mkview", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'viewobj':viewobj.__dict__})
	def delview(self,
		context=[],
		viewid=None):
                """
        Delete an existing view in a given context
        arguments:
                context - a list giving the path to the required context
                viewid - the id for the view
        returns:
                None on success
                """
		if viewid == None:
			raise ValueError, "delview: viewid is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "delview", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'viewid':viewid})

	
	def mkcontext(self, 
		context= [],
		contextobj=None):
		"""
	Make a new context in a given context
	arguments:
		context - a list giving the path to the required context 
		contextobj - a Context object
		"""
		if contextobj == None:
			raise ValueError, "mkcontext: contextobj is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "mkcontext", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'contextobj':contextobj.__dict__})


	def getcontext(self,
		context=[],
		getsize=False):
		"""
	Get context information
	arguments:
		context - a list giving the path to the required context
		getsize - True if the size in bytes of the context subtree is required
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "getcontext", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'getsize':getsize})

	def subscribe(self,
		context=[],
		view=None,
		subscription=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		view is either:
			an identifier of a view in the context specified
			a list of component identifiers or full path lists
			None indicating that the values of all components in
				the context be returned
			subscription is a Subscription object
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "subscribe", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'view':view,\
											    'subscription':subscription})
	def delete_sub(self,
		context=[],
		componentid=None,
		subname=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		componentid designates the component subscribed to
		subname is the subscription name
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file,  "delete_sub", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'componentid':componentid,\
											'subname':subname})

	def export_model(self,
		context=[],
		level=None,
		resolver=None):
		"""
	arguments:
		context is the context to export
                resolver is a string containing the name of a resolver
                        or
                resolver is a dictionary containing information about resolver(s) to be used and arguments
                        the "resolver" key gives the name of a resolver to use, if not present the default resolver is used
                        the "evidence_filter" key specifies an evidence filter
                        eg 'evidence_filter' =  "all" returns all evidence,
                                                "last10" returns last 10 evidence items,
                                                "last1" returns most recent evidence item,
                                                None returns no evidence
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "export_model", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'level':level,\
											'resolver':resolver})

	def import_model(self,
		context=[],
		partial_model=None):
		"""
	arguments:
		context is the context to import into
		partial_model is a json encoded string containing the partial model
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "import_model", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'partial_model':partial_model})
	def set_goals(self,
		context=[],
		componentid=None,
		goals=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		componentid designates the component with subscriptions attached
		goals is a list of paths to components that are:
			goals for this componentid if it is not of type goal
			components that contribute to this componentid if it is of type goal
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "set_goals", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentid':componentid,\
											    'goals':goals})

		
	def list_subs(self,
		context=[],
		componentid=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		componentid designates the component with subscriptions attached
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file,  "list_subs", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentid':componentid})

        def registerapp(self, app=None, desc="", fingerprint=None):
                """
                        registers an app as being authorised to access this user model
                        app name is a string (needs checking TODO)
                        app passwords are stored at the top level .model db
                """
		# Only users can register apps
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "registerapp", {'modelname':self.modelname,\
											    'authType':'user',\
											    'auth':self.auth,\
											    'app':app,\
											    'description':desc,\
											    'fingerprint':fingerprint})
	
	def deleteapp(self, app=None):
                """
                        deletes an app
                """
 		if app == None:
			raise ValueError, "deleteapp: app is None"
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "deleteapp", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'app':app})

	def listapps(self):
		"""
			returns array of registered app names
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "listapps", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth})

	def listrequests(self):
		"""
			returns array of apps requesting authorisation
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "listrequests", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth})

        def setpermission(self, context=None, componentid=None, app=None, permissions={}):
                """
                        sets ask/tell permission for a context (if componentid is None) or
                                a component
                """
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
 		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "setpermission", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context': context,\
											    'componentid': componentid,\
											    'app': app,\
											    'permissions': permissions})

	def getpermission(self, context=None, componentid=None, app=None):
                """
                        gets permissions for a context (if componentid is None) or
                                a component
                        returns a tuple (ask,tell)
                """
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, self.ca_certs_file, "getpermission", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context': context,\
											    'componentid': componentid,\
											    'app': app})

class Personis_server:
	def __init__(self, modeldir=None, cronq=None):
		self.modeldir = modeldir
		self.cronq = cronq

	def default(self, *args):
		try:
			jsonobj = cherrypy.request.body.read()
			print jsonobj
			pargs = json.loads(jsonobj)
		except:
                        print "bad request - cannot decode json - possible access from web browser"
                        return json.dumps("Personis User Model server. Not accessible using a web browser.")

		# dirty kludge to get around unicode
		for k,v in pargs.items():
			if type(v) == type(u''):
				pargs[k] = str(v)
			if type(k) == type(u''):
				del pargs[k]
				pargs[str(k)] = v

		try:			
			result = False
			if args[0] == 'mkmodel':
				# fixme need to implement security
				# and error handling
				
				# Only users can make models, so authType must be 'user'
				(user, password) = pargs['auth'].split(":")
				Personis_base.MkModel(model=pargs['modelname'], modeldir=self.modeldir, \
							user=user, password=password, description=pargs['description'])
				result = True
			elif args[0] == 'apprequestauth':
				Personis_base.AppRequestAuth(model=pargs['modelname'], modeldir=self.modeldir, \
							app=pargs['app'], key=pargs['key'], description=pargs['description'])
				result = True
			else:
				um = Personis_a.Access(model=pargs['modelname'], modeldir=self.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	
			if args[0] == 'access':
				result = True
			elif args[0] == 'tell':
				result = um.tell(context=pargs['context'], componentid=pargs['componentid'], evidence=Personis_base.Evidence(**pargs['evidence']))
			elif args[0] == 'ask':
				reslist = um.ask(context=pargs['context'], view=pargs['view'], resolver=pargs['resolver'], \
							showcontexts=pargs['showcontexts'])
				if pargs['showcontexts']:
					cobjlist, contexts, theviews, thesubs = reslist
					cobjlist = [c.__dict__ for c in cobjlist]
					for c in cobjlist:
						if c["evidencelist"]:
							c["evidencelist"] = [e for e in c["evidencelist"]]
					newviews = {}
					if theviews != None:
						for vname,v in theviews.items():
							newviews[vname] = v.__dict__
					else:
						newviews = None
					reslist = [cobjlist, contexts, newviews, thesubs]
				else:
					reslist = [c.__dict__ for c in reslist]
					for c in reslist:
						if c["evidencelist"]:
							c["evidencelist"] = [e for e in c["evidencelist"]]
				result = reslist

			elif args[0] == 'subscribe':
				result = um.subscribe(context=pargs['context'], view=pargs['view'], subscription=pargs['subscription'])
			elif args[0] == 'delete_sub':
				result = um.delete_sub(context=pargs['context'], componentid=pargs['componentid'], subname=pargs['subname'])
			elif args[0] == 'list_subs':
				result = um.list_subs(context=pargs['context'], componentid=pargs['componentid'])
			elif args[0] == 'export_model':
				result = um.export_model(context=pargs['context'], resolver=pargs['resolver'])
			elif args[0] == 'import_model':
				result = um.import_model(context=pargs['context'], partial_model=pargs['partial_model'])
			elif args[0] == 'set_goals':
				result = um.set_goals(context=pargs['context'], componentid=pargs['componentid'], goals=pargs['goals'])
			elif args[0] == 'registerapp':
				result = um.registerapp(app=pargs['app'], desc=pargs['description'], fingerprint=pargs['fingerprint'])
			elif args[0] == 'deleteapp':
				result = um.deleteapp(app=pargs['app'])
			elif args[0] == 'getpermission':
				result = um.getpermission(context=pargs['context'], componentid=pargs['componentid'], app=pargs['app'])
			elif args[0] == 'setpermission':
				result = um.setpermission(context=pargs['context'], componentid=pargs['componentid'], app=pargs['app'], permissions=pargs['permissions'])
			elif args[0] == 'listapps':
				result = um.listapps()
			elif args[0] == 'listrequests':
				result = um.listrequests()
			elif args[0] == 'mkcomponent':
				comp = Personis_base.Component(**pargs["componentobj"])
				result = um.mkcomponent(pargs["context"], comp)
			elif args[0] == 'delcomponent':
				result = um.delcomponent(pargs["context"], pargs["componentid"])
			elif args[0] == 'delcontext':
				result = um.delcontext(pargs["context"])
			elif args[0] == 'setresolver':
				result = um.setresolver(pargs["context"], pargs["componentid"], pargs["resolver"])
			elif args[0] == 'getresolvers':
				result = um.getresolvers()
			elif args[0] == 'mkview':
				viewobj = Personis_base.View(**pargs["viewobj"])
				result = um.mkview(pargs["context"], viewobj)
			elif args[0] == 'delview':
				result = um.delview(pargs["context"], pargs["viewid"])
			elif args[0] == 'mkcontext':
				contextobj = Personis_base.Context(**pargs["contextobj"])
				result = um.mkcontext(pargs["context"], contextobj)
			elif args[0] == 'getcontext':
				result = um.getcontext(pargs["context"], pargs["getsize"])

				
			# Repackage result code with error values IF there is a version string. 
			if pargs.has_key("version"):
				new_result = {}
				new_result["result"] = "ok"
				new_result["val"] = result
				result = new_result				
					
		except Exception, e:
			
			print "Exception:", e
			traceback.print_exc()
			if pargs.has_key("version"):
				new_result = {}
				#new_result["errorType"] = e.__class__.__name__
				#new_result["errorData"] = e.__dict__.copy()
				#new_result["pythonPickel"] = cPickle.dumps(e)
				new_result["val"] = [e.__class__.__name__, e.__dict__.copy(), cPickle.dumps(e)]
				new_result["result"] = "error"
				result = new_result
			else:
				result = False
		
		return json.dumps(result)
		
	default.exposed = True

if __name__ == '__main__':
	if len(sys.argv) == 2:
		modeldir = sys.argv[1]
	else:
		modeldir = 'models'
	cherrypy.root = Personis_server(modeldir)
	conf = os.path.join(os.path.dirname(__file__), 'personis_server.conf')
	cherrypy.config.update(conf)
	cherrypy.server.start()

