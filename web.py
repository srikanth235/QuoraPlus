
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
import json

from jinja2 import Environment, FunctionLoader, MemcachedBytecodeCache

from webapp2_extras import routes

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

# from helpers import FunctionLoader, jinja2_template_loader
# from helpers import jinja2_environment
from helpers import template_handler, json_handler

from model import *

class Main(webapp2.RequestHandler):
    def get(self):
          self.redirect("/html/index.html")

class CreateUser(webapp2.RequestHandler):
    def post(self):
          user, result = User.create_user(
                            email=self.request.get("email"),
                            password=self.request.get("password"),
                            first_name=self.request.get("first_name"),
                            last_name=self.request.get("last_name"))
          if result:
              self.response.out.write("Success")
          else:
              self.response.out.write("Failure")

class CreateCircle(webapp2.RequestHandler):
    def post(self, user_id=None):
        circle = Circle.create_circle(
                        description=self.request.get("description"),
                        email=self.request.get("email"),
                        name=self.request.get("name")
                    )
        if circle is None:
            self.response.out.write("Failure")
        else:
            self.response.out.write("Success")

class CreateQuestion(webapp2.RequestHandler):
    def post(self):
        circles = json.loads(self.request.get("circles"))
        question, result = Question.create_question(
                    email=self.request.get("email"),
                    description=self.request.get("description"),
                    circles=circles
                   )
        
        if result:
            id = question.key.id()
            self.response.out.write(question.key.id())
        else:
            self.response.out.write("Failure")

class CreateAnswer(webapp2.RequestHandler):
    def post(self):
        question_id = int(self.request.get("question_id"))
        answer, result = Answer.create_answer(
                        question_id=question_id,
                        email=self.request.get("email"),
                        description=self.request.get("description"),
                    )
        key = ndb.Key(Question, question_id)
        email = key.get().email
        Notification.create_notification(email=email,
                                         data=[self.request.get("email"), self.request.get("name")], 
                                         creator_email=self.request.get("email"),
                                         type=2)
        if result:
            self.response.out.write(answer.key.id())
        else:
            self.response.out.write("Success")


class CreateContact(webapp2.RequestHandler):
    def post(self):
        circles = json.loads(self.request.get("circles"))
        result = Contact.create_contact(
                        circles=circles,
                        email=self.request.get("email"),
                        user_email=self.request.get("user_email"),
                        name=self.request.get("name")
                    )
        qry = Contact.query(ndb.AND(Contact.email == self.request.get("email"),
                                     Contact.user_email == self.request.get("user_email"))).fetch()
        if len(qry) > 0:
            data = qry[0].circles
        result = Notification.create_notification(email=self.request.get("email"), 
                                         creator_email=self.request.get("user_email"),
                                         type=1,
                                         data=circles)
        if result:
            self.response.out.write("Success")
        else:
            self.response.out.write("Failure")
            
class MarkVote(webapp2.RequestHandler):
    def get(self):
        answer_id = int(self.request.get("answer_id"))
        state = int(self.request.get("state"))
        vote, result = Vote.create_or_update_vote(
                        answer_id=answer_id,
                        email=self.request.get("email"),
                        name=self.request.get("name"),
                        state=state
                    )
        if result:
            answer, status = Answer.update_vote_count(answer_id, vote.state)
            self.response.out.write(answer.parent.key.id())
        else:
            self.response.out.write("Failure")

class MarkFavorite(webapp2.RequestHandler):
    def post(self):
        favorite, result = Favorite.create_or_update_favorite(
                            email=self.request.get("email"),
                            question_id=int(self.request.get("question_id")))
        if result:
            self.response.out.write(favorite.question_ids)
        else:
            self.response.out.write("Failure")
    
class Login(webapp2.RequestHandler):
    def post(self):
        if User.is_valid_user(self.request.get("email"),
                              self.request.get("password")):
            self.response.out.write("Success")
        else:
            self.response.out.write("Failure")

class MainPage(webapp2.RequestHandler):
    @template_handler('index.html')
    def get(self):
        result = {}
        email = self.request.get("email")
        curs = Cursor(urlsafe=self.request.get("cursor"))
        circle = self.request.get("circle_name")
        question_list = []
        if self.request.get("want_favorites"):
            qry = Favorite.query(email==email).fetch()
            for row in qry:
                question_list.append(row.key().integer_id())
        if self.request.get("question_id"):
            question_list.append(int(self.request.get("question_id")))
        questions = Question.fetch_questions(email, curs, circle, question_list)
       # result["next_curs"] = next_curs
       # result["more"] = more
       # list = []
        
        #for tuple in questions:
            #question, top answer, # of answers, voters
         #   is_upvote = False
         #   voters = []
         #   for voter in tuple[3]:
         #       voters.append(voter.name)
         #       if email == voter.email:
         #           is_upvote = True
         #   is_favorite = Favorite.is_favorite(email, tuple[0].key.id())
         #   list.append([tuple[0], tuple[1], tuple[2], tuple[3], voters, is_upvote, is_favorite])
        #result["questions"] = list
        result["questions"] = ["what is testing"]
        circles = Circle.fetch_circles(email)
        pairs = []
        for question in questions:
            pairs.append([question, Answer.fetch_answer(question.key.id())])
        return {'questions' : pairs, 'circles' :circles}
        #path = os.path.join(os.path.dirname(__file__), '../Client/index.html')
        #self.response.out.write(template.render(path,
        #                          {'questions': result["questions"]
        #                          }))

class NotificationsPage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        curs = Cursor(urlsafe=self.request.get("cursor"))
        notifications, next_curs, more = Notification.fetch_unread_notifications(email, curs)
        result = {}
        result["notifications"] = notifications
        if next_curs is not None:
            result["next_curs"] = next_curs.url_safe()
        result["more"] = more
        self.response.out.write(json.dumps(result))

class ClearNotificationsPage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        return Notification.mark_as_read(email=email)

class FavoritePage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        
###### ROUTES and WSGI STUFF ######
url_routes = []
url_routes.append(
    routes.RedirectRoute(r'/',
                         handler=Main,
                         strict_slash=True,
                         name="main")
)

url_routes.append(
    routes.RedirectRoute(r'/create_user',
                         handler=CreateUser,
                         strict_slash=True,
                         name="create_user")
)

 
url_routes.append(
    routes.RedirectRoute(r'/create_circle',
                         handler=CreateCircle,
                         strict_slash=True,
                         name="create_circle")
)

url_routes.append(
    routes.RedirectRoute(r'/create_question',
                         handler=CreateQuestion,
                         strict_slash=True,
                         name="create_question")
)

url_routes.append(
    routes.RedirectRoute(r'/create_answer',
                         handler=CreateAnswer,
                         strict_slash=True,
                         name="create_answer")
)

 
url_routes.append(
    routes.RedirectRoute(r'/create_contact',
                         handler=CreateContact,
                         strict_slash=True,
                         name="create_contact")
)
 
url_routes.append(
    routes.RedirectRoute(r'/vote',
                         handler=MarkVote,
                         strict_slash=True,
                         name="vote")
)
 
url_routes.append(
    routes.RedirectRoute(r'/favorite',
                         handler=MarkFavorite,
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
