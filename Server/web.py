
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
        circles = simplejson.loads(self.request.get("circles"))
        result = Question.create_question(
                    email=user_id,
                    description=self.request.get("description"),
                    circles=circles
                   )
        
        if result:
            self.response.out.write("Success")
        else:
            self.response.out.write("Failure")

class CreateAnswer(webapp2.RequestHandler):
    def post(self, question_id=None):
        answer = Answer.create_answer(
                        question_id=int(question_id),
                        email=self.request.get("email"),
                        description=self.request.get("description"),
                    )
        key = ndb.Key(Question, int(question_id))
        email = key.get().email
        Notification.create_notification(email=email,
                                         data=[self.request.get("email"), self.request.get("name")], 
                                         creator_email=self.request.get("email"),
                                         type=2)
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
        cicle_names = simplejson.loads(self.request.get("circles"))
        contact = Contact.create_contact(
                        circle_names=circle_names,
                        contact_email=self.request.get("email"),
                        email=user_id,
                        name=self.request.get("name")
                    )
        qry = Contacts.query(ndb.AND(email=user_id, user_email=self.request.get("email"))).fetch()
        if len(qry) > 0:
            data = qry[0].circles
        Notification.create_notification(email=contact_email, creator_email=email, type=1, data=circles)
        if contact is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")
            
class MarkVote(webapp2.RequestHandler):
    def post(self, answer_id=None):
        vote = Vote.create_or_update_vote(
                        answer_id=answer_id,
                        email=self.request.get("email"),
                        name=self.request.get("name"),
                        state=self.request.get("state")
                    )
        if vote is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

class MarkFavorite(webapp2.RequestHandler):
    def post(self, user_id=None):
        favorite = Favorite.create_or_update_favorite(
                        email=user_id,
                        question_id=self.request.get("question_id")
                    )
        if favorite is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

def LoadHeader(email):
    result = {}
    result['no_of_notifications'] = fetch_no_of_unread_notifications(email)
    result['circles'] = fetch_circles(email) #projected only circle name
    return simplejson.dumps(result);
    
class Login(webapp2.RequestHandler):
    def post(self):
        if User.is_valid_user(self.request.get("email"),
                              self.request.get("password")):
            return LoadHeader(self.request.get("email"))
        else:
            self.response.out.write("Failure")

class MainPage(webapp2.RequestHandler):
    def post(self):
        results = {}
        email = self.request.get("email")
        curs = Cursor(urlsafe=self.request.get("cursor"))
        if self.request.get("circle_name"):
            circle = self.request.get("circle_name")
        else:
            circle = None
        question_list = []
        if self.request.get("want_favorites"):
            qry = Favorite.query(email==email).fetch()
            for row in qry:
                question_list.append(row.key().integer_id())
        if self.request.get("question_id"):
            question_list.append(int(self.request.get("question_id")))
        next_curs, more, questions = fetch_question(email, curs, circle, question_list)
        result["next_curs"] = next_curs
        result["more"] = more
        list = []
        for tuple in questions:
            #question, top answer, # of answers, voters
            is_upvote = False
            voters = []
            for voter in tuple[3]:
                voters.append(voter.name)
                if email == voter.email:
                    is_upvote = True
            is_favorite = Favorite.is_favorite(email, tuple[0].key.integer_id())
            list.append([tuple[0], tuple[1], tuple[2], tuple[3], voters, is_upvote, is_favorite])
        result["questions"] = list
        return simplejson.dumps(result)

class NotificationsPage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        curs = Cursor(urlsafe=self.request.get("cursor"))
        notifications, next_curs, more = Notification.fetch_unread_notifications(email)
        result = {}
        result["notifications"] = notifications
        result["next_curs"] = next_curs.url_safe()
        result["more"] = more
        return simplejson.dumps(result)

class ClearNotificationsPage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        return Notification.mark_as_read(email=email)

class FavoritePage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        
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
                         handler=Mark_Vote,
                         strict_slash=True,
                         name="vote")
)
 
url_routes.append(
    routes.RedirectRoute(r'/<user_id:\d+>/create_favorite',
                         handler=Mark_Favorite,
                         strict_slash=True,
                         name="favorite")
)

url_routes.append(
    routes.RedirectRoute(r'/login',
                         handler=Login,
                         strict_slash=True,
                         name="login")
)

url_routes.append(
    routes.RedirectRoute(r'/main',
                         handler=MainPage,
                         strict_slash=True,
                         name="main")
)

url_routes.append(
    routes.RedirectRoute(r'/notifications',
                         handler=NotificationsPage,
                         strict_slash=True,
                         name="notifications")
)

# 
# url_routes.append(
#     routes.RedirectRoute(r'/<user_id:\d+>/view_contacts',
#                          handler=ViewContacts,
#                          strict_slash=True,
#                          name="view_contacts")
# )
#  
app = webapp2.WSGIApplication(url_routes)
