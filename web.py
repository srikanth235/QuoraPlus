
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

from jinja2 import Environment, FunctionLoader, MemcachedBytecodeCache

from webapp2_extras import routes

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import channel

# from helpers import FunctionLoader, jinja2_template_loader
# from helpers import jinja2_environment
from helpers import template_handler, json_handler

from model import *

client_list = []

def broadcast(message, client_id=-1):
    clients = []
    if(client_id != -1 and client_id in client_list):
        clients = [client_id]
    else:
        clients = client_list
    for client_id in clients:
        channel.send_message(client_id, message)

def multicast(message, users):
    clients = list(set(client_list) & set(users))
    for client_id in clients:
        channel.send_message(client_id, message)

class AddClient(webapp2.RequestHandler):
    def post(self):
        global client_list
        client_id = self.request.get('from')
        if client_id not in client_list:
            client_list.append(self.request.get('from'))


class DeleteClient(webapp2.RequestHandler):
    def post(self):
        global client_list
        client_list.remove(self.request.get('from'))

class CreateUser(webapp2.RequestHandler):
    def post(self):
          user, result = User.create_user(
                            email=self.request.get("email"),
                            password=self.request.get("password"),
                            first_name=self.request.get("first_name"),
                            last_name=self.request.get("last_name"))

          if not result:
              self.response.out.write("Failure")

          else:
              circle, result = Circle.create_circle(
                        description="Universal List",
                        email=self.request.get("email"),
                        name="All Circles"
                    )
          self.redirect("/static/Login.html")

class DeleteUser(webapp2.RequestHandler):
    def post(self):
          user, result = User.delet_user(
                            email=self.request.get("email"))
          if result:
              self.response.out.write("Success")
          else:
              self.response.out.write("Failure")

class CreateCircle(webapp2.RequestHandler):
    def post(self):
        circle, result = Circle.create_circle(
                        description=self.request.get("description"),
                        email=self.request.get("email"),
                        name=self.request.get("name")
                    )
        if result:
            self.response.write("Success")
        else:
            self.response.out.write("Failure")

class CreateQuestion(webapp2.RequestHandler):
    def post(self):
        circles = (self.request.get("circles"))
        circles = circles.split(",")
        email = self.request.get("email")
        access_list = Contact.get_members_in_circles(circles, email)
        # adding self to the access list.
        if email not in access_list:
            access_list.append(email)
        name = User.get_user(email).name
        question, result = Question.create_question(
                    email=email,
                    description=self.request.get("description"),
                    circles=circles,
                    access_list=access_list,
                    name=name,
                    location=self.request.get("location")
                   )
        if result:
            id = question.key.id()
            message = json.dumps({
                        'type': 'question',
                        'question_id': id
                    })
            access_list.remove(email)
            multicast(message, access_list)
            self.response.out.write(question.key.id())
        else:
            self.response.out.write("Failure")

class CreateAnswer(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        question_id = int(self.request.get("question_id"))
        answer, result = Answer.create_answer(
                        question_id=question_id,
                        email=self.request.get("email"),
                        description=self.request.get("description"),
                        name=self.request.get("name")
                    )
        author_email = Question.get_author_email(question_id)
        Notification.create_notification(email=author_email,
                                         data=str(question_id),
                                         creator_email=email,
                                         creator_name=self.request.get("name"),
                                         type=2)
        if result:
            message = json.dumps({
                        'type': 'answer',
                        'question_id': question_id
                    })
            broadcast(message)
            self.response.out.write(answer.key.id())
        else:
            self.response.out.write("Failure")


class CreateContact(webapp2.RequestHandler):
    def post(self):
        if(User.get_user(self.request.get("email")) is None):
            self.response.out.write("Failure")
            return
        circles = (self.request.get("circles"))
        circles = circles.split(",")
        circles.append("All Circles")
        result = Contact.create_contact(
                        circles=circles,
                        data='',
                        email=self.request.get("email"),
                        user_email=self.request.get("user_email"),
                        name=self.request.get("name")
                    )
        result = Notification.create_notification(email=self.request.get("email"),
                                         creator_email=self.request.get("user_email"),
                                         creator_name=self.request.get("name"),
                                         type=1)
        if result:
            self.response.out.write("Success")
        else:
            self.response.out.write("Failure")

class ViewContacts(webapp2.RequestHandler):
    @template_handler('view_contacts.html')
    def get(self):
        contacts = Contact.fetch_contacts(self.request.get("email"))
        result = []
        return {'contacts': contacts}
         
class MarkVote(webapp2.RequestHandler):
    def post(self):
        answer_id = int(self.request.get("answer_id"))
        question_id = int(self.request.get("question_id"))
        vote, result = Vote.create_or_update_vote(
                        answer_id=answer_id,
                        email=self.request.get("email"),
                        name=self.request.get("name"),
                    )
        state = int(self.request.get("state"))
        if result:
            answer, status = Answer.update_vote_count(answer_id, question_id, state)
            message = json.dumps({
                        'type': 'vote',
                        'answer_id': answer_id,
                        'upvote_count': answer.upvote_count,
                        'question_id': question_id
                    })
            broadcast(message)            
            self.response.out.write(answer.upvote_count)
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
        user, result = User.is_valid_user(self.request.get("email"),
                              self.request.get("password"))
        if result:
            self.response.out.write(
                json.dumps({"name": user.name,
                            "email": user.email}))
        else:
            self.response.out.write("Failure")

class MainPage(webapp2.RequestHandler):
    @template_handler('check.html')
    def get(self):
        return {}

#same as home page except for disabling channels and returning JSON object directly
class TestHomePage(webapp2.RequestHandler):
    @template_handler('index.html')
    def get(self):
        result = {}
        email = self.request.get("email")
        result['circles'] = Circle.fetch_circles(email)
        result['favorites'] = Favorite.fetch_favorites(email)
        result['upvoted_answers'] = Vote.fetch_voted_answers(email)
        questions = []
        if self.request.get("question"): 
            result['mode'] = 1;
            questions.append(int(self.request.get("question")))
        else:
            result['mode'] = 0;
        if self.request.get("favorites"):
            questions = result['favorites']
        result['posts'] = []
        all_posts = Question.fetch_questions(email, questions)
        for question, answer in all_posts:
            if (len(questions) == 0 or question.key.id() in questions) and email in question.access_list:
                result['posts'].append((question, answer))
        result['email'] = email
        self.response.out.write(json.dumps(result))

class HomePage(webapp2.RequestHandler):
    @template_handler('index.html')
    def get(self):
        result = {}
        email = self.request.get("email")
        result['circles'] = Circle.fetch_circles(email)
        result['favorites'] = Favorite.fetch_favorites(email)
        result['upvoted_answers'] = Vote.fetch_voted_answers(email)
        questions = []
        if self.request.get("question"): 
            result['mode'] = 1;
            questions.append(int(self.request.get("question")))
        else:
            result['mode'] = 0;
        if self.request.get("favorites"):
            questions = result['favorites']
        result['posts'] = []
        all_posts = Question.fetch_questions(email, questions)
        for question, answer in all_posts:
            if (len(questions) == 0 or question.key.id() in questions) and email in question.access_list:
                result['posts'].append((question, answer))
        result['email'] = email
        channel_token = channel.create_channel(email)
        result['channel_token'] = channel_token
        return result

class NotificationsPage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        curs = Cursor(urlsafe=self.request.get("cursor"))
        notifications = Notification.fetch_unread_notifications(email, curs)
        result = {}
        result["notifications"] = notifications
        if next_curs is not None:
            result["next_curs"] = next_curs.url_safe()
        result["more"] = more
        self.response.out.write(json.dumps(result))

class ViewNotificationsPage(webapp2.RequestHandler):
    @template_handler('notifications.html')
    def get(self):
        email = self.request.get("email")
        notifications = Notification.fetch_notifications(email)
        result = {'notifications': notifications}
        return result

class ClearNotificationsPage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        return Notification.mark_as_read(email=email)

class FavoritePage(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")

class FetchCircles(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        circles = Circle.fetch_circles(email)
        result=[]
        for circle in circles:
            result.append(circle.name)
        self.response.out.write(json.dumps(result))
        
class CircleMembers(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        circle = self.request.get("circle")
        result = Contact.get_members_in_circles([circle], email)
        self.response.out.write(json.dumps(result))

###### ROUTES and WSGI STUFF ######
url_routes = []
url_routes.append(
    routes.RedirectRoute(r'/',
                         handler=MainPage,
                         strict_slash=True,
                         name="main")
)

url_routes.append(
    routes.RedirectRoute(r'/home',
                         handler=HomePage,
                         strict_slash=True,
                         name="home")
)

url_routes.append(
    routes.RedirectRoute(r'/testhome',
                         handler=TestHomePage,
                         strict_slash=True,
                         name="home")
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
    routes.RedirectRoute(r'/post_question',
                         handler=CreateQuestion,
                         strict_slash=True,
                         name="create_question")
)

url_routes.append(
    routes.RedirectRoute(r'/post_answer',
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
    routes.RedirectRoute(r'/view_contacts',
                         handler=ViewContacts,
                         strict_slash=True,
                         name="view_contact")
)
 
url_routes.append(
    routes.RedirectRoute(r'/mark_vote',
                         handler=MarkVote,
                         strict_slash=True,
                         name="vote")
)

url_routes.append(
    routes.RedirectRoute(r'/login',
                         handler=Login,
                         strict_slash=True,
                         name="login")
)

url_routes.append(
    routes.RedirectRoute(r'/notifications',
                         handler=NotificationsPage,
                         strict_slash=True,
                         name="notifications")
)

url_routes.append(
    routes.RedirectRoute(r'/view_notifications',
                         handler=ViewNotificationsPage,
                         strict_slash=True,
                         name="view_notifications")
)

url_routes.append(
    routes.RedirectRoute(r'/fetch_circles',
                         handler=FetchCircles,
                         strict_slash=True,
                         name="fetch_circles")
)

url_routes.append(
    routes.RedirectRoute(r'/mark_favorite',
                         handler=MarkFavorite,
                         strict_slash=True,
                         name="mark_favorite")
)

url_routes.append(
    routes.RedirectRoute(r'/circle_members',
                         handler=CircleMembers,
                         strict_slash=True,
                         name="circle_members")
)

url_routes.append(
    routes.RedirectRoute(r'/_ah/channel/connected/',
                         handler=AddClient,
                         strict_slash=True,
                         name="add_client")
)

url_routes.append(
    routes.RedirectRoute(r'/_ah/channel/disconnected/',
                         handler=DeleteClient,
                         strict_slash=True,
                         name="delete_client")
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
