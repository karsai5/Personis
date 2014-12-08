#!/usr/bin/env python

#
# The Personis system is copyright 2000-2011 University of Sydney
# Licenced under GPL v3
#


import sys
import cherrypy
import Personis_server
import Personis_base
from Personis_exceptions import *
import socket
import os
import argparse
import ConfigParser
from multiprocessing import Process, Queue
import cronserver

class Access(Personis_server.Access):

	def __init__(self, model = None, user=None, password=None, app=None, description="", configfile="~/.personis.conf", modelserver=None, debug=0):
		self.model = model
		self.debug = debug
		self.port = 2005
		self.hostname = 'localhost'
		self.modelname = model
		self.configfile = configfile
		self.configfile = os.path.expanduser(configfile)

		self.config = ConfigParser.ConfigParser()
		
		try: 
			self.config.readfp(open(self.configfile, "r"), self.configfile)
			self.port = self.config.get('personis_client', 'client.serverPort')
			self.ca_certs_file = self.config.get('personis_client', 'client.ca_certs_file')
		except: 
			pass

		try: 
			self.hostname = self.config.get('personis_client','client.serverHost')
			# hack to cope with different config parsers used by cherrypy and standard python
			if self.hostname[:1] in ['"',"'"] and  self.hostname[-1:] in ['"',"'"]:
				self.hostname = self.hostname[1:-1] # strip off quotes
		except: 
			pass

		try:
			(self.modelname, modelserver) = self.modelname.split('@')
		except:
			pass
		if modelserver == None:
			self.modelserver = self.hostname + ":" + str(self.port)
		else:
			self.modelserver = modelserver
		#print self.modelname, self.modelserver

		Personis_server.Access.__init__(self, model=self.modelname, modelserver=self.modelserver, user=user, password=password, app=app, description=description, debug=debug, ca_certs_file=self.ca_certs_file)


def runServer(modeldir, config):
	print "serving models in '%s'" % (modeldir)
	print "config file '%s'" % (config)
	print "starting cronserver"
#	cronserver.cronq = Queue()
	p = Process(target=cronserver.cronserver, args=(cronserver.cronq,modeldir))
	p.start()
	cherrypy.config.update(os.path.expanduser(config))
	port = cherrypy.config.get('server.socket_port')
	try:
		try:
			cherrypy.quickstart(Personis_server.Personis_server(modeldir))
		except Exception, E:
			print "Failed to run Personis Server:" + str(E)
	finally:
		print "Shutting down Personis Server."
		p.put(dict(op="quit"))
		p.join()

if __name__ == "__main__":
	aparser = argparse.ArgumentParser(description='Personis Server')
	aparser.add_argument('--models', help='directory holding models', default="Models")
        aparser.add_argument('--log', help='log file', default="stdout")
	aparser.add_argument('--config', help='config file for server', default='~/.personis_server.conf')
	args = aparser.parse_args(sys.argv[1:])
        if args.log != "stdout":
                sys.stdout = open(args.log, "w", 0)

	runServer(args.models, args.config)

