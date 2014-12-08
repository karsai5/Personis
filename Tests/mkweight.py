#!/usr/bin/env python

import Personis
import Personis_base
from Personis_util import printcomplist

um = Personis.Access(model="bob", user='bob')

weight = Personis_base.Component(Identifier="weight", Description="My weight", component_type="attribute", value_type="number")
um.mkcomponent(context=["Personal", "Health"], componentobj=weight)


