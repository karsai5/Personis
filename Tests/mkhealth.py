#!/usr/bin/env python

import Personis
import Personis_base
from Personis_util import printcomplist

um = Personis.Access(model="bob", user='bob')
Health = Personis_base.Context(Identifier="Health", Description="Health realated attributes")
um.mkcontext(context=["Personal"], contextobj=Health)


