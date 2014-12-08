

#!/usr/bin/env python2.4

#	David Carmichael 
# 	July 2006
#

''' Exceptions used in the Personis System '''

class ModelNotFoundError(IOError):
	"Used to indicate that no model can be found for given modelname"

class ModelServerError(IOError):
	"Used to indicate that the required model server is returning an error"

class AuthRequestedError(Exception):
	"Used to indicate that the app is not yet authorised but has requested authorisation"

class KeyFileNotFoundError(IOError):
	"Used to indicate that the private key file for an app does not exist"
