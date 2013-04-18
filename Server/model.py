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


class Question(ndb.Model):
    """Models an individual Question on  Quora+"""
    date_created = ndb.DateProperty(indexed=True, auto_now=True)
    description = ndb.TextProperty(indexed=True)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_question(cls, email, description):
        parent = ndb.Key(User, email)
        qry = Question.query(ndb.AND(Question.parent == parent,
                                     Question.description == description))

        if len(qry) == 0:
            question = Question(email=email,
                                password=password,
                                first_name=first_name,
                                last_name=last_name)
            question.key().parent = parent
            question.put()
            return True
        return False

class Notification(ndb.Model):
    """Models user notification on  Quora+"""
    date_created = ndb.DateProperty(indexed=True)
    description = ndb.StringProperty(indexed=True)
    is_read = ndb.BooleanProperty(default=False, indexed=True)
    @classmethod 
    @ndb.transactional(retries=1)
    def create_notification(cls, email, description):
        parent = ndb.Key(User, email)
        notification = Notification(description=description)
        notification.put()
        return True

    @classmethod 
    @ndb.transactional(retries=1)
    def mark_as_read(cls, email, identifier):
        key = ndb.Key(User, email, Notification, identifier)
        notification = key.get()
        notification.is_read = True
        notification.put()
        return True

class Circle(ndb.Model):
    """Models circle membership on  Quora+"""
    date_created = ndb.DateProperty(indexed=False, auto_now_add=True)
    description = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=True)

    @classmethod 
    @ndb.transactional(retries=1)
    def create_circle(cls, email, name, description):
        parent = ndb.Key(User, email)
        key = ndb.Key(Circle, name, parent=parent)
        if key.get() is None:
            circle = Circle(key=key,
                            description=description,
                            name=name)
            circle.put()
            return True
        return False

class Answer(Question):
    """Models answer on Quora+"""
    description = ndb.StringProperty(indexed=False)
    date_created = ndb.DateProperty(auto_now_add=True)
    email = ndb.StringProperty(indexed=True)

    @classmethod
    @ndb.transactional(retries=1)
    def create_answer(cls, question_id, author_email, description, email):
        parent = ndb.Key(Question, question_id, User, email)
        answer = Answer(description=description,
                        email=author_email
                        )
        answer.put()
        return True

class Vote(ndb.Model):
    """Models upvoting on Quora+"""
    email = ndb.StringProperty(indexed=True)
    state = ndb.IntegerProperty(indexed=True, default=1)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_vote(cls, answer_id, voter_email, email, question_id):
        parent = ndb.Key(User, email, Question, question_id, Answer, answer_id)
        key = ndb.Key(Vote, voter_email, parent=parent)
        if key.get() is None:
            vote = Vote(key=key, email=voter_email)
            vote.put()
        else:
            vote = key.get()
            vote.state = 1 - vote.state
            vote.put()
        return True

class Favorite(ndb.Model):
    """Models favorite on Quora+"""
    question_id = ndb.StringProperty(indexed=True)
    @classmethod
    @ndb.transactional(retries=1)
    def create_or_update_favorite(cls, email, question_id):
        parent = ndb.Key(User, email)
        key = ndb.Key(Favorite, question_id, parent=parent)
        if key.get() is None:
            favorite = Favorite(question_id=question_id)
            favorite.put()
        else:
            favorite = qry[0]
            favoite.key.delete()
        return True

class Share():
    """Models sharing to circles on Quora+"""
    circle_name = ndb.StringProperty(indexed=True)
    date_created = ndb.DateTimeProperty(indexed=False, auto_now=True)
    @classmethod
    @ndb.transactional(retries=1)
    def create_share(cls, circle_name, email, question_id):
        parent = ndb.Key(User, email, Question, question_id)
        key = ndb.Key(Share, circle_name, parent=parent)
        if key.get() is None:
            share = Share(key=key, circle_name=circle_name)
            share.put()
            return True
        return False

class Contact(User):
    """Models individual contacts on Quora+"""
    email = ndb.StringProperty(indexed=True)
    date_created = ndb.DateTimeProperty(indexed=True, auto_now=True)
    circle_names = ndb.StringProperty(repeated=True, indexed=False)
    @classmethod
    @ndb.transactional(retries=1)
    def create_contact(cls, circle_names, contact_email, email):
        parent = ndb.Key(User, email)
        key = ndb.Key(Contact, contact_email, parent=parent)
        if key.get() is None:
            contact = Contact(key=key, email=contact_email, cicle_names=circle_names)
            contact.put()
            return True
        return False
