#!/usr/bin/env python
import random
import unittest
import Personis_base

from Personis_util import printcomplist

class BaseTests(unittest.TestCase):
    
    def test_add_evidence_to_alice_model(self):

        # connect to personis instance
        um = Personis_base.Access(model="Alice", modeldir='Tests/Models', 
                authType='user', auth='alice:secret')

        # tell this as user alice's firstname, lastname and gender
        ev = Personis_base.Evidence(evidence_type="explicit", value="Alice")
        um.tell(context=["Personal"], componentid='firstname', evidence=ev)

        ev = Personis_base.Evidence(evidence_type="explicit", value="Smith")
        um.tell(context=["Personal"], componentid='lastname', evidence=ev)

        ev = Personis_base.Evidence(evidence_type="explicit", value="female")
        um.tell(context=["Personal"], componentid='gender', evidence=ev)
    
        # ask values from alice model
        name_resolved = um.ask(context=["Personal"], view='fullname', 
                resolver={'evidence_filter':"last1"})
        gender_resolved = um.ask(context=["Personal"], view='gender',
                resolver={'evidence_filter':'last1'})

        self.assertEqual(len(name_resolved), 2)
        self.assertEqual(name_resolved[0].value, 'Alice')
        self.assertEqual(name_resolved[1].value, 'Smith')

        self.assertEqual(len(gender_resolved), 1)
        self.assertEqual(gender_resolved[0].value, 'female')

if __name__ == '__main__':
    unittest.main()
