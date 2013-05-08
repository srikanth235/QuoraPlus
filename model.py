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
    screen_name = ndb.StringProperty(indexed=False)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_user(cls, email, password, first_name, last_name):
        key = ndb.Key(User, email)
        if key.get() is None:
            user = User(key=key,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        screen_name=first_name + " " + last_name)
            user.put()
            return user, True
        return None, False
    
    @classmethod 
    @ndb.transactional(retries=1)
    def delete_user(cls, email):
        key = ndb.Key(User, email)
        key.delete()
        return None, False

    @classmethod
    def is_valid_user(cls, email, password):
        key = ndb.Key(User, email)
        user = key.get()
        if user is None:
            return None, False
        elif password == user.password:
            return user, True
        return None, False
    
    @classmethod
    def get_user(cls, email):
        key = ndb.Key(User, email)
        user = key.get()
        return user

class Circle(ndb.Model):
    """Models circles on  Quora+"""
    date_created = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    description = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_circle(cls, name, email, description):
        key = ndb.Key(Circle, name + " " + email)
        if key.get() is None:
            circle = Circle(key=key,
                            description=description,
                            email=email,
                            name=name)
            circle.put()
            return circle, True
        return None, False

    @classmethod
    def fetch_circles(cls, email):
        circles = Circle.query(Circle.email == email).fetch()
        return circles

class Question(ndb.Model):
    """Models an individual Question on  Quora+"""
    date_created = ndb.DateTimeProperty(indexed=True, auto_now=True)
    description = ndb.TextProperty(indexed=True)
    circles = ndb.StringProperty(repeated=True)
    email = ndb.StringProperty(indexed=True)
    access_list= ndb.StringProperty(repeated=True, indexed=True)
    author=ndb.StringProperty(indexed=False)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_question(cls, email, description, circles, access_list, author):
        question = Question(email=email,
                            description=description,
                            circles=circles,
                            access_list=access_list,
                            author=author)
        question.put()
        return question, True
        

    @classmethod
    def fetch_questions(cls, email, curs, circle, question_ids):
        allowed_emails = []
        allowed_emails.append(email)
        #if question_ids is None:
        #qry, next_curs, more = Question.query(ndb.AND(len(set(circles).intersection(set(Question.circles))) > 0)).fetch_page(20, start_cursor = curs)
        qry = Question.query().fetch()
        rows = []
        for row in qry:
            #if len(set(circles).intersection(set(row.circles))):
                rows.append(row)  
        #else:
         #   qry, next_curs, more = Question.query(Question.key.id() in question_ids).fetch_page(20, start_cursor = curs)
        return rows
        #return next_curs, more, qry.map(Answer.callback)
        

class Notification(ndb.Model):
    """Models user notification on  Quora+"""
    date_created = ndb.DateTimeProperty(indexed=True, auto_now=True)
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
    def mark_as_read(cls, email, identifiers):
        notitifications = ndb.get_multi(identifiers)
        for notification in notifications:
            notification.is_read = True
            notification.put()
        return "Success"

    @classmethod
    def fetch_no_of_unread_notifications(cls, email):
         return len(Notification.query(ndb.AND(Notification.email==email, Notification.is_read==False)).fetch())
    
    @classmethod
    def fetch_unread_notifications(cls, email, curs=None):
        notifications, next_curs, more = Notification.query(ndb.AND(Notification.email==email, Notification.is_read==False)).fetch_page(20, start_cursor=curs)
        return notifications, next_curs, more

class Answer(Question):
    """Models answer on Quora+"""
    description = ndb.StringProperty(indexed=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty(indexed=True)
    upvote_count = ndb.IntegerProperty(default=0, indexed=True)
    question_id = ndb.IntegerProperty(indexed=True)
    
    def callback(self, question):
        answer = Answer.query(parent=question.key()).fetch().order(-Answer.upvote_count)
        answer_id = answer.key().integer_id()
        voters = Vote.fetch_voters(answer_id)
        return question, answer[0], len(answer), voters

    @classmethod
    @ndb.transactional(retries=1)
    def create_answer(cls, question_id, email, description):
        key = ndb.Key(Question, question_id)
        answer = Answer(parent=key,
                        description=description,
                        email=email,
                        question_id=question_id)
        answer.put()
        return answer, True
    @classmethod
    def fetch_answer(cls, question_id):
        answer = Answer.query(Answer.question_id == question_id).fetch()
        if len(answer) > 0:
            return answer[0]
        return None

    @classmethod
    @ndb.transactional(retries=1)
    def update_vote_count(cls, answer_id, state):
        key = ndb.Key(Answer, answer_id)
        answer = key.get()
        if state:
            answer.upvote_count = answer.upvote_count - 1
        else:
            answer.upvote_count = answer.upvote_count + 1
        answer.put()
        return answer, True

class Vote(ndb.Model):
    """Models upvoting on Quora+"""
    email = ndb.StringProperty(indexed=True)
    state = ndb.IntegerProperty(indexed=True, default=0) #0 upvote, 1 downvote
    answer_id = ndb.IntegerProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_vote(cls, answer_id, email, name, state):
        key = ndb.Key(Vote, str(answer_id) + " " + email)
        if key.get() is None:
           vote = Vote(key=key, email=email, answer_id=answer_id, name=name, state=state)
           vote.put()
        else:
            vote = key.get()
            vote.state = 1 - vote.state
            vote.put()
        return vote, True

    @classmethod
    def fetch_voters(cls, answer_id):
        return Vote.query(ndb.Query(Vote.answer_id==answer_id, Vote.state==1)).fetch(projection=[Vote.name, Vote.email])

class Favorite(ndb.Model):
    """Models favorite on Quora+"""
    question_ids = ndb.IntegerProperty(indexed=True, repeated=True)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_favorite(cls, email, question_id):
        key = ndb.Key(Favorite, email)
        if key.get() is None:
            favorite = Favorite(key=key, question_ids=[])
            favorite.question_ids.append(question_id)
            favorite.put()
        else:
            favorite = key.get()
            if question_id in favorite.question_ids:
                if len(favorite.question_ids) == 1:
                    favorite.question_ids = [-1]
                else:
                    favorite.question_ids.remove(question_id)
            else:
                favorite.questions_ids.append(question_id)
            favorite.put()
        return favorite, True

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
    name = ndb.StringProperty(indexed=False)
    @classmethod
    @ndb.transactional(retries=1)
    def create_contact(cls, circles, email, user_email, name):
        key = ndb.Key(Contact, email + " " + user_email)
        if key.get() is None:
            contact = Contact(key=key, email=email, user_email=user_email, name=name, circles=circles)
            contact.put()
            return True
        return False

    @classmethod
    def fetch_contacts(cls, email):
        return Contact.query(Contact.user_email == email).fetch()

    @classmethod
    def get_members_in_circles(cls, circles, email):
        contacts = Contact.query(Contact.user_email==email).fetch()
        result = []
        for contact in contacts:
            if len(list(set(contact.circles) & set(circles))) > 0:
                result.append(contact.email)
        return result