import unittest
import logging
import os
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

import webapp2

import web

class DemoTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Create a consistency policy that will simulate the High Replication consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testMain(self):
        request = webapp2.Request.blank('/')
        response = request.get_response(web.app)

        self.assertEqual(response.status_int, 200)

        os.environ['USER_EMAIL']='murph@murph.cc'
        os.environ['USER_ID']='1234'

        # See http://webapp-improved.appspot.com/guide/testing.html for how to setup the request
        request = webapp2.Request.blank('/')
        response = request.get_response(web.app)
        
        #Print out the response, so you can see it.
        logging.warn(response)

        os.environ['USER_EMAIL']='someone_else@murph.cc'
        os.environ['USER_ID']='1234'

        request = webapp2.Request.blank('/')
        response = request.get_response(web.app)

        #Print out the response again. Woah, look! We're someone else.
        logging.warn(response)

    

if __name__ == '__main__':
    unittest.main()
