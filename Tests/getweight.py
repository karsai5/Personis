#!/usr/bin/env python

import Personis
import Personis_base
from Personis_util import printcomplist

um = Personis.Access(model="bob", user='bob')

reslist = um.ask(context=["Personal", "Health"], view=['weight'], evidence_filter="all")
printcomplist(reslist, printev = "yes")

