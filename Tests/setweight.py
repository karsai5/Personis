#!/usr/bin/env python

import Personis
import Personis_base

um = Personis.Access(model="bob", user='bob')
ev = Personis_base.Evidence(source="withings", evidence_type="given", value="77.0")
um.tell(context=["Personal", "Health"], componentid='weight', evidence=ev)



