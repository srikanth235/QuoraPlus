#
# Copyright (c) 2013 Srikanth Srungarapu.
#
# Permission is granted to use this code for any purpose.
#
# This code is provided by the author 'as is' and comes without any
# warranty (Express, limited, or otherwise). In no event shall the
# author be liable for any damages or liability arising from the use
# of this code.
#


import logging
import os

from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

class User(ndb.Model):
    """Models an individual Quora+ User"""
    email = ndb.StringProperty(indexed=True)
    password = ndb.StringProperty(indexed=False)
    date_created = ndb.DateTimeProperty(indexed=False, auto_now=True)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_user(cls, email, password, first_name, last_name):
        key = ndb.Key(User, email)
        if key.get() is None:
            user = User(key=key,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name)
            user.put()
            return user
        return None

    @classmethod
    def is_valid_user(cls, self, email, password):
        key     = ndb.Key(User, email)
        user = key.get()
        if user is None:
            return False
        elif password == user.password:
            return True
        return False
    
    @classmethod
    def get_user(cls, email):
        key = ndb.Key(User, email)
        user = key.get()
        return user

class Question(ndb.Model):
    """Models an individual Question on  Quora+"""
    date_created = ndb.DateProperty(indexed=True, auto_now=True)
    description = ndb.TextProperty(indexed=True)
    circles = ndb.StringProperty(repeated=True)
    email = ndb.StringProperty(indexed=True)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_question(cls, email, description, circles):
        qry = Question.query(ndb.AND(Question.email == email,
                                     Question.description == description))

        if len(qry) == 0:
            question = Question(email=email,
                                description=description,
                                circles=circles)
            question.put()
            return True
        return False

    @classmethod
    def fetch_questions(cls, email, curs, circle, question_ids):
        allowed_emails = []
        if circle is None:
            qry = Contact.query(ndb.AND(Contact.user_email == email, circle in Contact.circles))
        else:
            qry = Contact.query(Contact.email == email)
        for row in qry:
            allowed_emails.append(row.email)

        qry = Contact.query(ndb.AND(contact.emal == email, contact.user_email in allowed_emails))
        circles = []
        for row in qry:
            circles.append(row.circles)
        if question_ids is None:
            qry, next_curs, more = Question.query(ndb.AND(len(set(circles).intersection(set(Question.circles))) > 0,
                                                          Question.email in allowed_emails)).fetch_page(20, start_cursor = curs)
        else:
            qry, next_curs, more = Question.query(Question.key().integer_id() in question_ids).fetch_page(20, start_cursor = curs)
        return next_curs, more, qry.map(Answer.callback)
        

class Notification(ndb.Model):
    """Models user notification on  Quora+"""
    date_created = ndb.DateProperty(indexed=True, auto_now_add=True)
    data = ndb.StringProperty(indexed=False, repeated=True)
    is_read = ndb.BooleanProperty(default=False, indexed=True)
    email = ndb.StringProperty(indexed=True)
    creator_email = ndb.StringProperty(indexed=False)
    type = ndb.IntegerProperty(indexed=True)  # 1 for addition, 2 for answering 

    @classmethod 
    @ndb.transactional(retries=1)
    def create_notification(cls, email, data, creator_email, type):
        notification = Notification(data=data, email=email,
                                    creator_email=creator_email, type=type)
        notification.put()
        return True

    @classmethod 
    @ndb.transactional(retries=1)
    def mark_as_read(cls, email, identifier=None):
        if identifier is None:
            notifications = Notification.query(ndb.AND(email==email, is_read==False))
        else:
            key = ndb.Key(Notification, identifier)
            notifications = [key.get()]
        for notification in notifications:
            notification.is_read = True
            notification.put()
        return "Success"

    @classmethod
    def fetch_no_of_unread_notifications(cls, email):
         return len(Notification.query(ndb.AND(email==email, is_read==False)))
    
    @classmethod
    def fetch_unread_notifications(cls, email):
        notifications, next_cur, more = Notifications.query(ndb.AND(email==email, is_read==False)).fetch_page(20, start_cursor=curs)
        return notifications, next_cur, more

class Circle(ndb.Model):
    """Models circles on  Quora+"""
    date_created = ndb.DateProperty(indexed=False, auto_now_add=True)
    description = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_circle(cls, name, email, description):
        qry = Circle.query(ndb.AND(Circle.name == name, email == email))
        if len(qry) == 0:
            circle = Circle(description=description,
                            email = email,
                            name=name)
            circle.put()
            return True
        return False

    @classmethod
    def fetch_circles(cls, email):
        qry = Circle.query(Circle.email == email).fetch(projection=[Circle.name])
        return qry

class Answer(Question):
    """Models answer on Quora+"""
    description = ndb.StringProperty(indexed=False)
    date_created = ndb.DateProperty(auto_now_add=True)
    email = ndb.StringProperty(indexed=True)
    upvote_count = ndb.IntegerProperty(default=0, indexed=True)

    def callback(self, question):
        answer = Answer.query(parent=question.key()).fetch().order(-Answer.upvote_count)
        answer_id = answer.key().integer_id()
        voters = Vote.fetch_voters(answer_id)
        return question, answer[0], len(answer), voters

    @classmethod
    @ndb.transactional(retries=1)
    def create_answer(cls, question_id, email, description):
        parent = ndb.Key(Question, question_id)
        answer = Answer(description=description,
                        email=email)
        answer.put()
        return True

class Vote(ndb.Model):
    """Models upvoting on Quora+"""
    email = ndb.StringProperty(indexed=True)
    state = ndb.IntegerProperty(indexed=True, default=1) #1 upvote, 0 downvote
    answer_id = ndb.IntegerProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_vote(cls, answer_id, email, name, state):
        qry = Vote.query(ndb.AND(Vote.email == email,
                                 Vote.answer_id == answer_id))
        if len(qry) == 0:
            vote = Vote(email=voter_email, answerd_id=answer_id, name=name, state=state)
            vote.put()
        else:
            vote = qry[0]
            vote.state = 1 - vote.state
            vote.put()
        return True

    @classmethod
    def fetch_voters(cls, answer_id):
        return Vote.query(ndb.Query(Vote.answer_id==answer_id, Vote.state==1)).fetch(projection=[Vote.name, Vote.email])

class Favorite(ndb.Model):
    """Models favorite on Quora+"""
    question_ids = ndb.StringProperty(indexed=True, repeated=True)
    email = ndb.StringProperty(indexed=True)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_favorite(cls, email, question_id):
        key = ndb.Key(User, email)
        if key.get() is None:
            favorite = Favorite(question_ids=[question_id])
            favorite.put()
        else:
            favorite = key.get()
            if question_id in favorite.question_ids:
                favorite.question_ids = favorite.question_ids.remove(question_id)
            else:
                favorite.questions_ids.append(question_id)
            favorite.put()
        return True

    @classmethod
    def is_favorite(cls, email, question_id):
        favorites = Favorite.query(Favorite.email==email).question_ids
        return question_id in favorites

class Contact(User):
    """Models individual contacts on Quora+"""
    email = ndb.StringProperty(indexed=True)
    date_created = ndb.DateTimeProperty(indexed=True, auto_now=True)
    circles = ndb.StringProperty(repeated=True, indexed=False)
    user_email = ndb.StringProperty(indexed=True)
    @classmethod
    @ndb.transactional(retries=1)
    def create_contact(cls, circles, email, user_email, name):
        qry = Contact.query(ndb.AND(Contact.email == email,
                                    Contact.user_email == user_email))
        if len(qry) == 0:
            contact = Contact(email=email, user_email=user_email, name=name, cicles=circles)
            contact.put()
            return True
        return False
