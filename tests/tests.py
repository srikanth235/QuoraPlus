import unittest
import logging
import os
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

import webapp2

import web
import json

from model import *

class DemoTestCase(unittest.TestCase):
    def createUser(self, email, first_name, last_name, password):
        user, result = User.create_user(email, first_name, last_name, password)

    def createCircle(self, name, email, description):
        circle,resul = Circle.create_circle(name, email, description)
    
    def createQuestion(self, email, description, circles, access_list, name, location):
        question, result = Question.create_question(email, description, circles, access_list, name, location)
        self.question_id = question.key.id()

    def createAnswer(self, question_id, email, description, name):
        answer, result = Answer.create_answer(question_id, email, description, name)
        self.answer_id = answer.key.id()

    def createContact(self, circles, email, user_email, name):
        result = Contact.create_contact(circles, email, user_email, name)

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
        #setting up test data
        self.email = "srikanth235@gmail.com"
        self.first_name = "Srikanth"
        self.last_name = "Srungarapu"
        self.password = "123"
        self.secondary_email = "vishnu.90.priya@gmail.com"
        self.last_email = "srungar2@illinois.edu"
        
        self.circle_name = "CS498"
        self.circle_description = "Web Programming classmates"
        self.name = "Srikanth Srungarapu"
        
        self.question_description = "What is web programming?"
        self.answer_description = "Magic :)"
        self.access_list = ["srikanth235@gmail.com"] 
        self.location = "Champaign"
        self.createUser(self.email, self.first_name, self.last_name, self.password)
        self.createUser(self.secondary_email, "", "", "")
        self.createUser(self.last_email, self.first_name, self.last_name, self.password)
        self.createContact([], self.last_email, self.email, self.name)
        self.createCircle(self.circle_name, self.email, self.circle_description)
        self.createQuestion(self.email, self.question_description, ["CS498"], [self.email], self.name, self.location)
        self.createAnswer(self.question_id, self.email, self.answer_description, self.name)

    def tearDown(self):
        self.testbed.deactivate()

    def testCreateUser(self):
        params = {}
        params["email"] = "testing1@gmail.com"
        params["password"] = "test"
        params["first_name"] = "First"
        params["last_name"] = "Last"
        request = webapp2.Request.blank(path='/create_user', POST=params)
        response = request.get_response(web.app)
        # on creation of user redirect action takes place
        self.assertEqual(response.status_int, 302)
    
    def testCreateCircle(self):
        params = {}
        params["email"] = self.email
        params["description"] = "Testing"
        params["name"] = "Test"
        request = webapp2.Request.blank(path='/create_circle', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "Success", "Circle creation failed")
    
    def testPostQuestion(self):
        params = {}
        params["circles"] = self.circle_name
        params["description"] = "Will this test pass?"
        params["email"] = self.email
        params["location"] = self.location
        request = webapp2.Request.blank(path='/post_question', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertNotEqual(response.body, "Failure", "Posting Question failed")
   
    def testPostAnswer(self):
        params = {}
        params["circles"] = self.circle_name + "," +"All Circles"
        params["description"] = "Absolutely, yes"
        params["email"] = self.email
        params["name"] = self.name
        params["question_id"] = self.question_id
        request = webapp2.Request.blank(path='/post_answer', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertNotEqual(response.body, "Failure", "Posting Answer failed")

    def testCreateContact(self):
        params = {}
        params["circles"] = self.circle_name
        params["email"] = "testing@gmail.com"
        params["name"] = "tester"
        params["user_email"] = self.email
        request = webapp2.Request.blank(path='/create_contact', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "Failure", "Creating contact failed")
        params["email"] = self.secondary_email
        request = webapp2.Request.blank(path='/create_contact', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "Success", "Creation of contact successful")
    
    def testVote(self):
        params = {}
        params["email"] = "testing@gmail.com"
        params["question_id"] = self.question_id
        params["answer_id"] = self.answer_id
        params["name"] = self.name
        params["state"] = 1
        request = webapp2.Request.blank(path='/mark_vote', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "1", "Upvoting failed")
        params["state"] = -1
        request = webapp2.Request.blank(path='/mark_vote', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "0", "Downvoting failed")

    def testVote(self):
        params = {}
        params["email"] = "testing@gmail.com"
        params["question_id"] = self.question_id
        params["answer_id"] = self.answer_id
        params["name"] = self.name
        params["state"] = 1
        request = webapp2.Request.blank(path='/mark_vote', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "1", "Upvoting failed")
        params["state"] = -1
        request = webapp2.Request.blank(path='/mark_vote', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "0", "Downvoting failed")

    def testFavorite(self):
        params = {}
        params["email"] = "testing@gmail.com"
        params["question_id"] = self.question_id
        request = webapp2.Request.blank(path='/mark_favorite', POST=params)
        response = request.get_response(web.app)
        answer ="[" + str(self.question_id) + "]"
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, answer, "Marking as favorite failed")
        params["state"] = -1
        request = webapp2.Request.blank(path='/mark_favorite', POST=params)
        response = request.get_response(web.app)
        answer = "[]"
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, answer, "Unmarking as favorite failed")
    
    def testAccessControl(self):
        params = {}
        params["circles"] = self.circle_name
        params["description"] = "Will this test pass?"
        params["email"] = self.email
        params["location"] = self.location
        request = webapp2.Request.blank(path='/post_question', POST=params)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertNotEqual(response.body, "Failure", "Posting Question failed")
        request = webapp2.Request.blank(path='/testhome?email=' + self.last_email)
        response = request.get_response(web.app)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.find("posts:[]"), -1, "Access control failed")
    
if __name__ == '__main__':
    unittest.main()
