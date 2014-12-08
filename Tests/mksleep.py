#!/usr/bin/env python

import Personis
import Personis_base
from Personis_util import printcomplist

um = Personis.Access(model="bob", user='bob')

sleep = Personis_base.Component(Identifier="sleep", Description="Sleep info", component_type="attribute", value_type="string")
um.mkcomponent(context=["Personal", "Health"], componentobj=sleep)


