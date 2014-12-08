

Security Architecture
=====================

This section describes the Personis security architecture. There are two
different methods for authentication: one for users and one for apps. Users
have a password-based system and apps use an RSA keypair and digital
signatures. 

When authenticating, there are two parameters sent to the server (or the
Personis library): authType and auth. authType is a string and must be one of
either "user" or "app". auth is also a string and consists of a colon-separated
tuple containing either the username and password (for users) or the app name,
signing string and signature (for apps). However, developers using the Personis
library do not need to set these parameters and can instead supply either a
username and password, or an app name and optionally a description when creating
a Personis.Access object.  See the examples in the sections below for details.

Server
-----

Connections to a Personis server are secured using SSL. This means the server
must have a certificate in order to authenticate it to the client. See the
Server section for more details. Currently server certificates are not being
validated; this needs to be enabled in jsoncall.py and will not work for a
self-signed certificate unless it is installed on the client system.

User login
----------

Users authenticate with their username and password (set when a model is
created). The password is hashed using SHA256 and stored. On login, the password
the user sends is again hashed and compared to the stored value.::

        um = Personis.Access(model="alice", user="Alice", password="secret") 

App login
---------

Since apps need to be able to login without interaction from the user,
especially in the case of apps running on sensors or other embedded devices,
apps use an RSA keypair and digital signatures to authenticate. When an app
first runs, a keypair (2048 bits) is generated. The app must have write access
to the directory in which it is run for this to occur. The keypair will be
stored in a file named <app_name>_key.pem.

Next, access to the given user model is requested. This occurs when an app
attempts to create a Personis.Access object without already having access to the
requested user model. A fingerprint of the app's public key is sent to the
server and an AuthRequestedError is raised. This exception can be printed to
display the app's fingerprint to the user. The user must authorise the app and
give it appropriate permissions before it is able to access the model. The user
can check that the app's fingerprint matches to ensure they are authorising the
correct app.

On subsequent logins, the app instead uses a digital signature to prove that it
is in fact the authorised app, with access to the matching private key. This
occurs each time the app sends a command to the Personis server. First, the
command (string) is hashed. This is then concatenated with a
(cryptographic-quality) nonce and a timestamp, signed, and sent to the server.
The server checks that the signature is valid for the app's public key, that the
timestamp falls within a ten-minute window of the current time and that the
nonce has not been seen before. The sliding time window is used so that the
server needn't store every nonce ever seen - only those within the valid window.

Most of this process is carried out automatically when a Personis.Access object
is created and thus an app developer need not perform the above steps
themselves.::

        try:
                um = Personis.Access(model="alice", modelserver="localhost:2005", \
                        app="flashcards", description="A simple flashcard study app")
        except AuthRequestedError as e:
                print e
                print "Please authorise the app and then run it again."
                exit()
        except:
                print "Unable to access user model %s on server %s" % (model, server)
 
