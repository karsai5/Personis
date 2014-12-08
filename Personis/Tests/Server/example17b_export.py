#!/usr/bin/env python

import sys
import Personis
from Personis_util import printcomplist, printjson

# export a model sub tree to JSON

um = Personis.Access(model="Alice", user='alice', password='secret')
modeljson = um.export_model(["Personal"], resolver=dict(evidence_filter="all"))
printjson(modeljson)

um.import_model(context=["Temp"], partial_model=modeljson)

modeljson = um.export_model(["Personal"], resolver=dict(evidence_filter="all"))
printjson(modeljson)
