#!/usr/bin/env python
import Personis_a
import Personis_base
import cStringIO
import contextlib
import os
import random
import shutil
import sys
import unittest

from Personis_util import printcomplist, showobj
from Personis_mkmodel import *

class SimpleTests(unittest.TestCase):

    def setUp(self):
        deleteModels('Alice')
        with nostdout():
            createAliceModel()
        self.um = Personis_base.Access(model='Alice', modeldir='Tests/Models', 
                authType='user', auth='alice:secret')
        self.give_alice_details()

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
        self.um = Personis_base.Access(model='Alice', modeldir='Tests/Models', 
                authType='user', auth='alice:secret')

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
        # access model
        self.um = Personis_base.Access(model='Alice', modeldir='Tests/Models', 
                authType='user', auth='alice:secret')

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
        # TODO: work out what this is doing
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

    def test_show_contex(self):
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

        um = Personis_base.Access(model="Alice", modeldir='Tests/Models', authType='user', auth='alice:secret')

        # 1. Show the root context
        info = um.ask(context=[""], showcontexts=True)
        # printAskContext(info) # uncomment for more details about context
        (cobjlist, contexts, theviews, thesubs) = info # enter tuple info in variables
        self.assertEqual(contexts, ['Location', 'Personal', 'Temp', 'Work', 
            'Devices', 'People', 'Preferences', 'modelinfo'])
        self.assertEqual(theviews, {})
        self.assertEqual(thesubs, {})

        # 2. Show the Personal context
        info = um.ask(context=["Personal"], showcontexts=True)
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
            Personis_base.AppRequestAuth(model='Alice', modeldir='Tests/Models', 
                    app='MyHealth', key=key.publickey().exportKey(), 
                    description="My Health Manager")
        except Exception as e:
            print "App auth request failed with exception : %s\n" % (e)

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


@contextlib.contextmanager
def nostdout():
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
    
def createAliceModel():
    """
    Creates the alice model, outputs a lot of text, recommemded you use with
    the nostdout contextmanager
    """
    modelserver = None
    auth = user + ':' + password
    print modeldir + '/Alice'
    mkmodel(model=mname, mfile=mfile, modeldir=modeldir, user=user, 
            password=password)

def deleteModels(modelName):
    """
    Deletes the passed model name from the model directory
    """
    deletedir = modeldir + '/' + modelName
    if os.path.exists(deletedir):
        shutil.rmtree(deletedir)


if __name__ == '__main__':
    # connect to personis instance
    mname = 'Alice'
    user = 'alice'
    password = 'secret'
    mfile = 'Src/Modeldefs/user'
    modeldir = 'Tests/Models'

    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
