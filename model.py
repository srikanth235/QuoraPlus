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
    name = ndb.StringProperty(indexed=False)

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
                        name=first_name + " " + last_name)
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
    name=ndb.StringProperty(indexed=False)
    location=ndb.StringProperty(indexed=True)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_question(cls, email, description, circles, access_list, name, location):
        question = Question(email=email,
                            description=description,
                            circles=circles,
                            access_list=access_list,
                            name=name,
                            location=location)
        question.put()
        return question, True


    @classmethod
    def fetch_questions(cls, email, question_ids):
        qry = Question.query().order(-Question.date_created)
        if len(question_ids) == 0:
            return qry.map(single_answer_callback)
        else:
            return qry.map(multipe_answers_callback)

    @classmethod
    def get_author_email(cls, question_id):
        key = ndb.Key(Question, question_id)
        return key.get().email

class Notification(ndb.Model):
    """Models user notification on  Quora+"""
    date_created = ndb.DateTimeProperty(indexed=True, auto_now=True)
    data = ndb.StringProperty(indexed=False)
    is_read = ndb.BooleanProperty(default=False, indexed=True)
    email = ndb.StringProperty(indexed=True)
    creator_email = ndb.StringProperty(indexed=False)
    creator_name = ndb.StringProperty(indexed=True)
    type = ndb.IntegerProperty(indexed=True)  # 1 for addition, 2 for answering 

    @classmethod 
    @ndb.transactional(retries=1)
    def create_notification(cls, email, data, creator_email, type, creator_name):
        notification = Notification(email=email, data=data, creator_email=creator_email, type=type, creator_name=creator_name)
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
    def fetch_notifications(cls, email, curs=None):
        notifications = Notification.query(Notification.email==email).fetch()
        return notifications

class Answer(Question):
    """Models answer on Quora+"""
    description = ndb.StringProperty(indexed=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty(indexed=True)
    upvote_count = ndb.IntegerProperty(default=0, indexed=True)
    question_id = ndb.IntegerProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)

    @classmethod
    @ndb.transactional(retries=1)
    def create_answer(cls, question_id, email, description, name):
        key = ndb.Key(Question, question_id)
        answer = Answer(parent=key,
                        description=description,
                        email=email,
                        question_id=question_id,
                        name=name)
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
    def update_vote_count(cls, answer_id, question_id, state):
        key = ndb.Key(Question, question_id, Answer, answer_id)
        answer = key.get()
        if answer:
            answer.upvote_count = answer.upvote_count + state
            answer.put()
            return answer, True
        return None, False

class Vote(ndb.Model):
    """Models upvoting on Quora+"""
    email = ndb.StringProperty(indexed=True)
    answer_ids = ndb.IntegerProperty(repeated=True)
    name = ndb.StringProperty(indexed=False)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_vote(cls, answer_id, email, name):
        key = ndb.Key(Vote, email)
        if key.get() is None:
           vote = Vote(key=key, email=email, answer_ids=[answer_id], name=name)
           vote.put()
        else:
            vote = key.get()
            answer_ids = vote.answer_ids
            if answer_id in answer_ids:
                answer_ids.remove(answer_id)
            else:
                answer_ids.append(answer_id)
            vote.answer_ids = answer_ids
            vote.put()
        return vote, True

    @classmethod
    def fetch_voted_answers(self, email):
        key = ndb.Key(Vote, email)
        if key.get() is None:
            return []
        else:
            return key.get().answer_ids

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
            question_ids = favorite.question_ids
            if question_id in question_ids:
                question_ids.remove(question_id)
                favorite.question_ids = question_ids
            else:
                question_ids = favorite.question_ids
                question_ids.append(question_id)
                favorite.questions_ids = question_ids
            favorite.put()
        return favorite, True

    @classmethod
    def fetch_favorites(cls, email):
        key = ndb.Key(Favorite, email)
        if key.get() is None:
            return []
        else:
            return key.get().question_ids

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
    
def multipe_answers_callback(question):
    answers = Answer.query(ancestor=question.key).order(-Answer.date_created).fetch()
    return question, answers

def single_answer_callback(question):
    answer = Answer.query(ancestor=question.key).order(-Answer.date_created).fetch(1)
    return question, answer