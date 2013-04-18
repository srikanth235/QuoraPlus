
#
# Copyright (c) 2013 Srikanth Srungarapu, Vishnu Priya
#
# Permission is granted to use this code for any purpose.
#
# This code is provided by the author 'as is' and comes without any
# warranty (Express, limited, or otherwise). In no event shall the
# author be liable for any damages or liability arising from the use
# of this code.
#

import logging
import json
import os
import random
import webapp2
import simplejson

from jinja2 import Environment, FunctionLoader, MemcachedBytecodeCache

from webapp2_extras import routes

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb


# from helpers import FunctionLoader, jinja2_template_loader
# from helpers import jinja2_environment
# from helpers import template_handler, json_handler

from model import *

class Main(webapp2.RequestHandler):
    def get(self):
          self.response.out.write("Hello, Welcome to Quora+")

class CreateUser(webapp2.RequestHandler):
    def post(self):
          user = User.create_user(
                    email=self.request.get("email"),
                    password=self.request.get("password"),
                    first_name=self.request.get("first_name"),
                    last_name=self.request.get("last_name"))
          if user is None:
              self.response.out.write("Failure")
          else:
              self.respone.out.write("Success")

class CreateQuestion(webapp2.RequestHandler):
    def post(self, user_id=None):
        question = Question.create_question(
                    email=user_id,
                    description=self.request.get("description")
                   )
        question_id = question.key().id()
        circles_list = simplejson.loads(self.request.get("circles_list"))
        for circle_name in circles_list:
            share = create_share(
                    circle_name=circle_name,
                    email=email,
                    question_id=question_id
                    )
            if share is None:
                self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

class CreateAnswer(webapp2.RequestHandler):
    def post(self, question_id=None):
        answer = Answer.create_answer(
                        question_id=question_id,
                        author_email=self.request.get("author_email"),
                        description=self.request.get("description"),
                        email=self.request.get("email")
                    )
        if answer is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

class CreateCircle(webapp2.RequestHandler):
    def post(self, question_id=None):
        circle = circle.create_answer(
                        question_id=question_id,
                        description=self.request.get("description"),
                        email=self.request.get("email")
                    )
        if circle is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

class CreateContact(webapp2.RequestHandler):
    def post(self, user_id=None):
        cicle_names = simplejson.loads(self.request.get("circle_names"))
        contact = Contact.create_contact(
                        circle_names=circle_names,
                        contact_email=self.request.get("email"),
                        email=user_id
                    )
        if contact is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")
            
class Vote(webapp2.RequestHandler):
    def post(self, answer_id=None):
        vote = Vote.create_or_update_vote(
                        answer_id=answer_id,
                        voter_email=self.request.get("voter_email"),
                        email=self.request.get("email"),
                        question_id=question_id
                    )
        if vote is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

class Favorite(webapp2.RequestHandler):
    def post(self, answer_id=None):
        favorite = favorite.create_or_update_favorite(
                        answer_id=answer_id,
                        voter_email=self.request.get("voter_email"),
                        email=self.request.get("email"),
                        question_id=self.request.get("question_id")
                    )
        if favorite is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")
###### ROUTES and WSGI STUFF ######
url_routes = []
# url_routes.append(
#     routes.RedirectRoute(r'/',
#                          handler=Main,
#                          strict_slash=True,
#                          name="main")
# )

url_routes.append(
    routes.RedirectRoute(r'/create_user',
                         handler=CreateUser,
                         strict_slash=True,
                         name="create_user")
)

url_routes.append(
    routes.RedirectRoute(r'/<email:\.+>/create_question',
                         handler=CreateQuestion,
                         strict_slash=True,
                         name="create_question")
)

url_routes.append(
    routes.RedirectRoute(r'/<question_id:\d+>/create_answer',
                         handler=CreateAnswer,
                         strict_slash=True,
                         name="create_answer")
)
 
url_routes.append(
    routes.RedirectRoute(r'/<user_id:\d+>/create_circle',
                         handler=CreateCircle,
                         strict_slash=True,
                         name="create_circle")
)
 
url_routes.append(
    routes.RedirectRoute(r'/<user_id:\d+>/create_contact',
                         handler=CreateContact,
                         strict_slash=True,
                         name="create_contact")
)
 
url_routes.append(
    routes.RedirectRoute(r'/<answer_id:\d+>/vote',
                         handler=Vote,
                         strict_slash=True,
                         name="vote")
)
 
url_routes.append(
    routes.RedirectRoute(r'/<user_id:\d+>/favorite',
                         handler=Favorite,
                         strict_slash=True,
                         name="favorite")
)
# 
# url_routes.append(
#     routes.RedirectRoute(r'/<user_id:\d+>/view_contacts',
#                          handler=ViewContacts,
#                          strict_slash=True,
#                          name="view_contacts")
# )
#  
# url_routes.append(
#     routes.RedirectRoute(r'/<question_id:\d+>',
#                          handler=ViewQuestion,
#                          strict_slash=True,
#                          name="view_question")
# )

app = webapp2.WSGIApplication(url_routes)
