#!/usr/bin/env python
import cStringIO
import contextlib
import os
import random
import shutil
import sys
import unittest
import json

import Personis_a
import Personis_base
from Personis_util import printcomplist, showobj, printjson
from Personis_mkmodel import *

class SimpleTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # connect to personis instance
        cls.mname = 'Alice'
        cls.user = 'alice'
        cls.password = 'secret'
        cls.mfile = os.path.dirname(os.path.realpath(__file__)) + '/../Src/Modeldefs/user'
        cls.modeldir = os.path.dirname(os.path.realpath(__file__)) + '/Models'

    def setUp(self):
        self.deleteModels('Alice')
        with self.nostdout():
            self.createAliceModel()
        self.um = Personis_base.Access(model='Alice', modeldir=self.modeldir, 
                authType='user', auth='alice:secret')
        self.give_alice_details()

    @contextlib.contextmanager
    def nostdout(self):
        """
        Can be used to run function without printint to std out.
        eg. 
            with nostdout():
                foo()
        """
        save_stdout = sys.stdout
        sys.stdout = cStringIO.StringIO()
        yield
        sys.stdout = save_stdout
        
    def createAliceModel(self):
        """
        Creates the alice model, outputs a lot of text, recommemded you use with
        the nostdout contextmanager
        """
        modelserver = None
        auth = self.user + ':' + self.password
        mkmodel(model=self.mname, mfile=self.mfile, modeldir=self.modeldir, user=self.user, 
                password=self.password)

    def deleteModels(self,modelName):
        """
        Deletes the passed model name from the model directory
        """
        deletedir = self.modeldir + '/' + modelName
        if os.path.exists(deletedir):
            shutil.rmtree(deletedir)


    def give_alice_details(self):
        """
        Enter firstname, lastname and gender into alice model        
        """
        ev = Personis_base.Evidence(evidence_type='explicit', value='Alice')
        self.um.tell(context=['Personal'], componentid='firstname', evidence=ev)

        ev = Personis_base.Evidence(evidence_type='explicit', value='Smith')
        self.um.tell(context=['Personal'], componentid='lastname', evidence=ev)

        ev = Personis_base.Evidence(evidence_type='explicit', value='female')
        self.um.tell(context=['Personal'], componentid='gender', evidence=ev)

    def test_add_evidence_to_alice_model(self):
        """
        Check that the correct values where entered from the give_alice_details 
        function.
        """
        name_resolved = self.um.ask(context=['Personal'], view='fullname', 
                resolver={'evidence_filter':'last1'})
        gender_resolved = self.um.ask(context=['Personal'], view='gender',
                resolver={'evidence_filter':'last1'})

        self.assertEqual(len(name_resolved), 2)
        self.assertEqual(name_resolved[0].value, 'Alice')
        self.assertEqual(name_resolved[1].value, 'Smith')

        self.assertEqual(len(gender_resolved), 1)
        self.assertEqual(gender_resolved[0].value, 'female')

    def test_ask_evidence_from_alice_model(self):
        """
        Ask for a series of pieces of evidence from the model using custom views
        """

        # 1. Ask for alices name
        reslist = self.um.ask(context=['Personal'], view='fullname')
        self.assertEqual(len(reslist), 2)
        self.assertEqual(reslist[0].value, 'Alice')
        self.assertEqual(reslist[1].value, 'Smith')

        # 2. ask for alice's first then last name

        res = self.um.ask(context=['Personal'], view=['firstname', 'lastname'])
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].value, 'Alice')
        self.assertEqual(res[1].value, 'Smith')

        # 3. ask for alice's gender
        res = self.um.ask(context=['Personal'], view=['gender'])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].value, 'female')

        # 4. ask for alice's artist preferences

        reslist = self.um.ask(context=['Preferences', 'Music', 'Jazz', 'Artists'], 
                view=['Miles_Davis'])
        self.assertEqual(len(reslist), 1)
        self.assertEqual(reslist[0].value, None)

        # 5. ask for all the components in the Personal context - 5 of them

        reslist = self.um.ask(context=['Personal'])
        self.assertEqual(len(reslist), 4)
        self.assertEqual(reslist[0].value, None) # check email
        self.assertEqual(reslist[1].value, 'Alice') # check first name
        self.assertEqual(reslist[2].value, 'female') # check gender
        self.assertEqual(reslist[3].value, 'Smith') # check last name

    def test_change_alice_name(self):
        """
        Change Alice's name to Carrol
        """

        # create a piece of evidence with Carrol as value
        ev = Personis_base.Evidence(evidence_type="explicit", value="Carrol")
        self.um.tell(context=["Personal"], componentid='firstname', evidence=ev)
        ev = Personis_base.Evidence(evidence_type="explicit", value="Smith")
        self.um.tell(context=["Personal"], componentid='lastname', evidence=ev)

        reslist = self.um.ask(context=["Personal"], view='fullname', 
                resolver={'evidence_filter':'last1'})
        self.assertEqual(reslist[0].value, 'Carrol')
        self.assertEqual(reslist[1].value, 'Smith')

    def test_add_music_preference(self):
        """
        Add a musical preferece for Miles_Davis
        """
        ev = Personis_base.Evidence(evidence_type="explicit", value=4)
        self.um.tell(context=["Preferences", "Music","Jazz","Artists"], 
                componentid='Miles_Davis', evidence=ev)

        reslist = self.um.ask(context=["Preferences", "Music", "Jazz", "Artists"], 
                view=['Miles_Davis'], resolver={'evidence_filter':"all"})
        self.assertEqual(len(reslist), 1)
        self.assertEqual(reslist[0].value, 4)

    def test_complex_view(self):
        # Todo: Work out what complex_view test is doing
        # print "ask for the components in a more complex view of a preference and Alice's first name"
        # ev = Personis_base.Evidence(evidence_type="explicit", value=4)
        # self.um.tell(context=["Preferences", "Music","Jazz","Artists"], 
        #         componentid='Miles_Davis', evidence=ev)
        # # get component objects for a more complex view
        # # in this case the first component is "Miles_Davis" in 
        # # the nominated context, the second component is 
        # # "firstname" in the "Personal" context
        # um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='user', auth='alice:secret')
        # reslist = um.ask(context=["Preferences", "Music", "Jazz", "Artists"], 
        #     view=['Miles_Davis', ['Personal', 'firstname']], resolver={'evidence_filter':"all"})

        # print "==================================================================="
        # print "Now check the evidence list for that view"
        # printcomplist(reslist, printev = "yes")

        # res2 = um.ask(context=["Personal"], view=["firstname"], resolver={'evidence_filter':"all"})
        # print "==================================================================="
        # printcomplist(res2, printev = "yes")
        self.assertTrue(True)

    def test_add_and_remove_component(self):
        """
        Add and remove a new component(age) to Alice model
        """
        # create a new component
        cobj = Personis_base.Component(Identifier="age", component_type="attribute", 
                Description="age", goals=[['Personal', 'Health', 'weight']], 
                value_type="number")
        # add it to modal
        res = self.um.mkcomponent(context=["Personal"], componentobj=cobj)

        # show this age in the Personal context
        ev = Personis_base.Evidence(evidence_type="explicit", value=17)
        self.um.tell(context=["Personal"], componentid='age', evidence=ev)
        reslist = self.um.ask(context=["Personal"], view=['age'], 
                resolver={'evidence_filter':"all"})
        self.assertEqual(len(reslist), 1)
        self.assertEqual(reslist[0].value, 17)
        resd = self.um.delcomponent(context=["Personal"], componentid = "age")
        with self.assertRaises(ValueError):
            reslist = self.um.ask(context=["Personal"], view=['age'], 
                    resolver={'evidence_filter':"all"})
            self.assertEqual(len(reslist), 1)

    def test_add_and_remove_view(self):
        """
        Add and remove a custom view that shows alice's firstname lastname and email
        """
        # create a new view in a given context
        vobj = Personis_base.View(Identifier="email_details", 
                component_list=["firstname", "lastname", "email"])
        self.um.mkview(context=["Personal"], viewobj=vobj)
        reslist = self.um.ask(context=["Personal"], view = 'email_details', 
                resolver={'evidence_filter':"all"})
        self.assertEqual(len(reslist), 3)
        self.assertEqual(reslist[0].value, 'Alice')
        self.assertEqual(reslist[1].value, 'Smith')
        self.assertEqual(reslist[2].value, None)

        # delete view
        self.um.delview(context=['Personal'], viewid = 'email_details')
        with self.assertRaises(ValueError):
            self.um.ask(context=['Personal'], view = 'email_details',
                    resolver = {'evidence_filter'})

    def test_add_new_resolver(self):
        """
        Add two new resolver functions, must be done locally as you cant add 
        resolver functions from a remote client.
        The first function returns the correct details.
        The brokenresolver returns an empty component for age regardless of
        what information is been resolved
        """

        def brokenresolver(model=None, component=None, context=None, resolver_args=None):
            """     new resolver function 
            """
            if resolver_args == None:
                ev_filter = None
            else:
                ev_filter = resolver_args.get('evidence_filter')
            component.evidencelist = component.filterevidence(model=model, 
                    context=context, resolver_args=resolver_args)
            if len(component.evidencelist) > 0:
                component.value = component.evidencelist[-1]['value']
            return Personis_base.Component(Identifier="age", 
                    component_type="attribute", Description="age", 
                    goals=[['Personal', 'Health', 'weight']], value_type="number")

        def myresolver(model=None, component=None, context=None, resolver_args=None):
            """     new resolver function, returns incorrect new age component
            """
            if resolver_args == None:
                ev_filter = None
            else:
                ev_filter = resolver_args.get('evidence_filter')
            component.evidencelist = component.filterevidence(model=model, 
                    context=context, resolver_args=resolver_args)
            if len(component.evidencelist) > 0:
                component.value = component.evidencelist[-1]['value']
            return component

        self.um.resolverlist["myresolver"] = myresolver
        self.um.resolverlist["brokenresolver"] = brokenresolver

        # use normal resolver
        reslist = self.um.ask(context=["Personal"], view='fullname', 
                resolver={"resolver":"myresolver", "evidence_filter":"all"})
        self.assertEqual(len(reslist), 2)
        self.assertEqual(reslist[0].value, 'Alice')
        self.assertEqual(reslist[1].value, 'Smith')

        reslist = self.um.ask(context = ['Personal'], view = 'fullname',
                resolver = {'resolver':'brokenresolver'})
        self.assertEqual(len(reslist), 2)
        self.assertEqual(reslist[0].value, None)
        self.assertEqual(reslist[1].value, None)
        self.assertEqual(reslist[0].Description, 'age')
        self.assertEqual(reslist[1].Description, 'age')

    def test_tell_location(self):
        # create a piece of evidence with home as value
        ev = Personis_base.Evidence(evidence_type="explicit", value="home")
        # tell this as user alice's location
        self.um.tell(context=['Location'], componentid='location', evidence=ev)

        reslist = self.um.ask(context=['Location'], view=['location'], resolver={'evidence_filter':"all"})
        self.assertEqual(len(reslist), 1)
        self.assertEqual(reslist[0].value, 'home')

    def test_show_context(self):
        """
        Shows information about the context such as, sub-contexts, views for 
        that context and subscriptions to the context.

        If you want to view more information about the contexts, uncomment the 
        printAskContext lines
        """

        def printAskContext( info ):
            (cobjlist, contexts, theviews, thesubs) = info
            # printcomplist(cobjlist, printev = "yes")
            print "Contexts: %s" % str(contexts)
            print "Views: %s" % str(theviews)
            print "Subscriptions: %s" % str(thesubs)

        # 1. Show the root context
        info = self.um.ask(context=[""], showcontexts=True)
        # printAskContext(info) # uncomment for more details about context
        (cobjlist, contexts, theviews, thesubs) = info # enter tuple info in variables
        self.assertEqual(contexts, ['Location', 'Personal', 'Temp', 'Work', 
            'Devices', 'People', 'Preferences', 'modelinfo'])
        self.assertEqual(theviews, {})
        self.assertEqual(thesubs, {})

        # 2. Show the Personal context
        info = self.um.ask(context=["Personal"], showcontexts=True)
        # printAskContext(info) # uncomment for more details about context
        (cobjlist, contexts, theviews, thesubs) = info # enter tuple info in variables
        self.assertEqual(contexts, ['Health'])

    def test_create_app_and_test_permissions(self):
        """
        Creates an app called MyHealth and gives it ask but not tell permissions.
        Ask for the permissions of an unregistered app as well as deleting the 
        original MyHealth app.
        """

        # Create an app
        try:
            key = Personis_base.generate_app_key("MyHealth")
            fingerprint = Personis_base.generate_app_fingerprint(key)
            Personis_base.AppRequestAuth(model='Alice', modeldir=self.modeldir, 
                    app='MyHealth', key=key.publickey().exportKey(), 
                    description="My Health Manager")
        except Exception as e:
            self.fail("App auth request failed with exception : %s\n" % (e))

        # Check fingerprints match
        requests = self.um.listrequests()
        fingerprint2 = requests['MyHealth']['fingerprint']

        if fingerprint2 != fingerprint:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        # Register app
        appdetails = self.um.registerapp(app="MyHealth", desc="My Health Manager", 
                fingerprint=fingerprint)

        # Check app was registered
        apps = self.um.listapps()
        self.assertEqual(apps, {'MyHealth': {'description': 'My Health Manager'}})

        # Give app permissions
        self.um.setpermission(context=["Personal"], app="MyHealth", 
                permissions={'ask':True, 'tell':False})

        # Check permissions are correct
        perms = self.um.getpermission(context=["Personal"], app="MyHealth")
        self.assertEqual(perms['ask'], True)
        self.assertEqual(perms['tell'], False)
        
        # Delete the MyHealth app
        try:
                self.um.deleteapp(app="MyHealth")
        except Exception as e:
                print "deleteapp failed with exception : %s\n" % (e)

        # Check there's no registered apps
        apps = self.um.listapps()
        self.assertEqual(apps, {})

    def test_get_permissions_of_unregistered_app(self):
        """ 
        Simply asks for the permissions of an app that hasn't been registered
        """

        # Ask for permissions of unregistered app, should throw ValueError
        with self.assertRaises(ValueError):
            perms = self.um.getpermission(context=['Personal'], app='withings')

    def test_using_permissions_to_access_data(self):
        """ 
        AS an extension of the test_create_app_and_test_permissions test, this test
        creates and app and registers it, it then uses this app to access different,
        bits of information such as name etc. and confirms that the correct 
        information is given in accordance to the apps permissions
        """

        # Check there's no registered apps
        apps = self.um.listapps()
        self.assertEqual(apps, {})

        # Try and set permissions on a context for an unregistered app:
        with self.assertRaises(ValueError):
            self.um.setpermission(context=["Personal"], app="MyHealth", 
                    permissions={'ask':True, 'tell':False})

        # Register MyHealth
        try:
            key = Personis_base.generate_app_key("MyHealth")
            fingerprint = Personis_base.generate_app_fingerprint(key)
            Personis_base.AppRequestAuth(model='Alice', modeldir=self.modeldir, 
                    app='MyHealth', key=key.publickey().exportKey(), 
                    description="My Health Manager")
        except Exception as e:
            self.fail("App auth request failed with exception : %s\n" % (e))

        requests = self.um.listrequests()
        fingerprint2 = requests['MyHealth']['fingerprint']

        if fingerprint2 != fingerprint:
            self.fail("Fingerprints don't match!")

        appdetails = self.um.registerapp(app="MyHealth", desc="My Health Manager", 
                fingerprint=fingerprint)

        apps = self.um.listapps()
        self.assertEqual(apps, {'MyHealth': {'description': 'My Health Manager'}})

        # Give the MyHealth app permissions
        self.um.setpermission(context=["Personal"], app="MyHealth", 
                permissions={'ask':False, 'tell':False, 
                    "resolvers":["last1", "goal"]})

        # Check those permissions
        perms = self.um.getpermission(context=["Personal"], app="MyHealth")
        self.assertEqual(perms, {'ask': False, 'resolvers': ['last1', 'goal'], 
            'tell': False})

        # Change name to Alex Jones
        ev = Personis_base.Evidence(evidence_type="explicit", value="Alex")
        self.um.tell(context=["Personal"], componentid='firstname', evidence=ev)
        ev = Personis_base.Evidence(evidence_type="explicit", value="Jones")
        self.um.tell(context=["Personal"], componentid='lastname', evidence=ev)

        # Ask for Alice's fullname as owner (should work)
        # Check the name was changed
        reslist = self.um.ask(context=["Personal"], view='fullname')
        self.assertEqual(len(reslist), 2)
        self.assertEqual(reslist[0].value, 'Alex')
        self.assertEqual(reslist[1].value, 'Jones')

        # Access Alice's model as an unregistered App
        self.um = None
        with self.assertRaises(ValueError):
            unregistered_key = Personis_base.generate_app_key("MyHealth")
            auth = 'withings:' + Personis_base.generate_app_signature('withings', unregistered_key)
            self.um = Personis_base.Access(model="Alice", modeldir=self.modeldir, authType='app', auth=auth)

        # Access Alice's model as a registered App (should work)
        self.um = None
        try:
            auth = 'MyHealth:' + Personis_base.generate_app_signature('MyHealth', key) 
            self.um = Personis_base.Access(model="Alice", modeldir=self.modeldir, authType='app', auth=auth)
        except Exception as e:
            self.fail("Access failed with exception : %s\n" % (e))

        # Ask for Alice's fullname as app 'MyHealth' (should NOT work)
        with self.assertRaises(ValueError):
            reslist = self.um.ask(context=["Personal"], view='fullname')

        # Set ask permission for the 'MyHealth' app
        self.um = None
        self.um = Personis_base.Access(model="Alice", modeldir=self.modeldir, authType='user', auth='alice:secret')
        self.um.setpermission(context=["Personal"], app="MyHealth", permissions={'ask':True, 'tell':False})


        # Ask for Alice's fullname as app 'MyHealth' (should work now)
        self.um = None
        auth = 'MyHealth:' + Personis_base.generate_app_signature('MyHealth', key) 
        self.um = Personis_base.Access(model="Alice", modeldir=self.modeldir, authType='app', auth=auth)
        try:
            reslist = self.um.ask(context=["Personal"], view='fullname')
            self.assertEqual(len(reslist), 2)
            self.assertEqual(reslist[0].value, 'Alex')
            self.assertEqual(reslist[1].value, 'Jones')
        except Exception as e:
            self.fail("ask failed with exception : %s\n" % (e))

        # Now try and tell a new value for first name (should NOT work)
        ev = Personis_base.Evidence(evidence_type="explicit", value="Fred")
        with self.assertRaises(ValueError):
            self.um.tell(context=["Personal"], componentid='firstname', evidence=ev)

        # Delete the 'MyHealth' app while NOT accessing as owner
        with self.assertRaises(ValueError):
            self.um.deleteapp(app="MyHealth")

        # Delete the 'MyHealth' app while accessing as owner
        self.um = None
        self.um = Personis_base.Access(model="Alice", modeldir=self.modeldir, authType='user', auth='alice:secret')
        try:
            self.um.deleteapp(app="MyHealth")
        except Exception as e:
            self.fail("deleteapp failed with exception : %s\n" % (e))

        # List the registered apps (should be none)
        apps = self.um.listapps()
        self.assertEqual(apps,{})

    def test_add_json_content_to_component(self):
        """
        Adds a person to the People component using just a json object 
        """

        # add a JSON encoded value to a component
        fullname = {'firstname':'James', 'lastname':'Bond'}
        # create a piece of evidence with json encoded value
        ev = Personis_base.Evidence(evidence_type="explicit", value=json.dumps(fullname))
        self.um.tell(context=["People"], componentid='fullname', evidence=ev)

        # Now check the evidence list
        reslist = self.um.ask(context=["People"], view=['fullname'])
        self.assertEqual(len(reslist), 1)
        self.assertEqual(reslist[0].value, 
                '{"lastname": "Bond", "firstname": "James"}')

    def test_output_json(self):

        um = Personis_a.Access(model="Alice", modeldir=self.modeldir, 
                authType='user', auth='alice:secret')
        # export a model sub tree to JSON
        with self.nostdout():
            modeljson = um.export_model(["Personal"], resolver="default")
        #modeljson = um.export_model(["Personal"])
        # printjson(modeljson)

        with self.nostdout():
            um.import_model(context=["Temp"], partial_model=modeljson)
        #um.import_model(partial_model=modeljson)

        modeljson = um.export_model(["Temp"])
        # printjson(modeljson)

    def test_output_json2(self):

        # export a model sub tree to JSON

        um = Personis_a.Access(model="Alice", modeldir=self.modeldir, 
                authType='user', auth='alice:secret')
        with self.nostdout():
            modeljson = um.export_model(["Personal"], resolver=dict(evidence_filter="all"))
        # printjson(modeljson)

        with self.nostdout():
            um.import_model(context=["Temp"], partial_model=modeljson)

        self.fail("Currently, exporting a model doesn't export views")

    def test_goals(self):
        """
        Add goals to alice's model as well as some evidence
        """
        cobj = Personis_base.Component(Identifier="fitness", component_type="goal", 
                Description="My overall fitness", 
                goals=[['Personal', 'Health', 'weight']], value_type="number")

        # Add weight goal
        res = self.um.mkcomponent(context=["Personal"], componentobj=cobj)
        res = self.um.ask(context=['Personal'], view=['fitness'])
        self.assertEqual(res[0].goals, [['Personal', 'Health', 'weight']])

        # Add evidence to weight goal
        ev = Personis_base.Evidence(evidence_type="explicit", value=17)
        self.um.tell(context=["Personal"], componentid='fitness', evidence=ev)
        reslist = self.um.ask(context=["Personal"], view=['fitness'], 
                resolver={'evidence_filter':"all"})
        self.assertEqual(reslist[0].value, 17)

        # Add extra 'steps' goal
        goals = reslist[0].goals
        goals.append(["Personal", "Health", "steps"])
        self.um.set_goals(context=["Personal"], componentid='fitness', goals=goals)
        reslist = self.um.ask(context=["Personal"], view=['fitness'], resolver={'evidence_filter':"all"})
        self.assertEqual(reslist[0].goals, [['Personal', 'Health', 'weight'], 
            ['Personal', 'Health', 'steps']])

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
