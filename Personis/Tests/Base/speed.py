#!/usr/bin/env python

import Personis_base 
from Personis_util import showobj, printcomplist


um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='user', auth='alice:secret')


for i in range(100000):
	res = um.ask(context=["Personal"], view=['gender'])
