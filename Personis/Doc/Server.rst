
Personis Server
===============

Personis operates as a library that is imported by application programs and stores models in the local file
system.

Personis can also be run as a server, providing an interface to models for remote clients. In this case the API is almost the same, the only difference being the modules that is imported and used for the Access call, and the
specification of the model to be accessed.

In the case of locally stored models, access requires a *modeldir* argument to specify the 
location of the stored models, as well as the name of the model (a simple ID). 
For models accessed remotely via the server, *modeldir* is not used and the model name has the form:
name@server[:port].

For example, to access the model for "alice" stored on the server "models.server.com" we 
would use the statements::

	import Personis

	um = Personis.Access(model="alice@models.server.com", user='myapp', password='pass')

Running a Server
----------------

It is very easy to run your own Personis server to provide access to models for remote clients.

A server gets configuration information from the file $HOME/.personis_server.conf.
This file specifies the port that the server is to use as well as some miscellaneous configuration options.
A suitable personis_server.conf file can be found in the Personis/Src directory. This can be copied into 
$HOME/.personis_server.conf and the port number changed as desired.

A server can be started for any set of models stored in the same directory using the command::

	# assuming that PYTHONPATH, MODELDIR and LOGFILE are initialised
	Personis.py  --models $MODELDIR --log $LOGFILE &

The directory containing the models is specified in $MODELDIR.
Log information is written to $LOGFILE. This includes information on all requests, error messages etc.

Since communications between the server and client use SSL, the server needs an
SSL certificate. This can be a self-signed certificate, which you can generate
using OpenSSL or other tool of your choice. See the following section for more
information on obtaining and using OpenSSL.

There are three configuration options relating to SSL that can be set in
$HOME/.personis_server.conf. The first is the SSL module to use for the server.
We recommend PyOpenSSL, however if you wish you can specify a different module
and this will be used by CherryPy instead. The other two parameters are the
server's SSL certificate file and the file containing the corresponding private
key. The defaults are personis_server_cert.pem and personis_server_priv.key, in
the same directory the server is run from. Below is an example of setting these
options (in this case we set them to the default values).::

        server.ssl_module = "pyopenssl"
        server.ssl_certificate = "./personis_server_cert.pem"
        server.ssl_private_key = "./personis_server_priv.key"

Note that paths for the SSL certificate and private key files are relative to
the directory in which the server is run.

Generating Keys and Certificates Using OpenSSL
..............................................

OpenSSL can be downloaded from http://www.openssl.org/ or installed using your
system's package manager. Documentation for OpenSSL can be found at
http://www.openssl.org/docs/ and should be used as the primary reference.
However, for convenience we provide below some instructions on generating keys
and self-signed certificates. More detailed information on this process can be
found at http://www.openssl.org/docs/HOWTO/certificates.txt

To generate a key and certificate in one command, you can use the following:::

        $ openssl req -x509 -newkey rsa:2048 -keyout personis_server_priv.key \
        -out personis_server_cert.pem -days 365

This will generate a new 2048-bit RSA keypair and create a self-signed
certificate using this key. The certificate will expire after 365 days. You can
change the type of key, key size, expiry time and filenames as you wish - see
the OpenSSL manpage for the options available.

If you wish to have your certificate signed by an external certificate authority
(recommended for production servers), you can then send the cert.pem file to the
certificate authority. You will need to ensure that the Common Name you specify
when creating the certificate exactly matches the domain you will be using.

Once you have your private key and certificate, you need to move these files to
the directory you will run the server from, or fully specify their location in
the Personis server config file.
