
import httplib, httplib2, types, cPickle
import simplejson as json
from urllib import urlencode

http = None
currentServer = None

def do_call(server, port, ca_certs_file, fun, args):
	global http, currentServer
	args["version"] = "11.2"
	args_json = json.dumps(args) + '\n'
	if http == None or (server + ":" + str(port) != currentServer):
		http = httplib2.Http(disable_ssl_certificate_validation=True)
		currentServer = server + ":" + str(port)
	uri = "https://" + server + ":" + str(port) + "/" + fun + "?"
	res, res_json = http.request(uri, "POST", args_json)
	logfile = open("json.log", "w")
	logfile.write(res_json)
	logfile.write("\n")
	logfile.close()
#	con = httplib.HTTPConnection(server, port)
#	con.request("POST", "/"+fun, args_json)
#	res = con.getresponse()
#	res_json =  res.read()
#	con.close()
#	res_json = res_json.split("\n")[0]
	try:
		result = json.loads(res_json)
	except:
		print "json loads failed!"
		print "<<%s>>" % (res_json)
		raise ValueError, "json loads failed"
	# dirty kludge to get around unicode
	for k,v in result.items():
		if type(v) == type(u''):
			result[k] = str(v)
		if type(k) == type(u''):
			del result[k]
			result[str(k)] = v
	## Unpack the error, and if it is an exception throw it.
	if type(result) == types.DictionaryType and result.has_key("result"):
		if result["result"] == "error":
			print result
			# We have returned with an error, so throw it as an exception.
			if result.has_key("pythonPickel"):
				raise cPickle.loads(result["pythonPickel"])
			elif len(result["val"]) == 3:
				raise cPickle.loads(str(result["val"][2]))
			else:
				raise Exception, str(result["val"])
		else:
			# Unwrap the result, and return as normal. 
			result = result["val"]
        return result
