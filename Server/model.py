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
    key_name = ndb.StringProperty(indexed=True)
    password = ndb.StringProperty(indexed=False)
    date_created = ndb.DateProperty(indexed=False)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)

class Question(User):
    date_created = ndb.DateProperty(indexed=False)
    description = ndb.TextProperty(auto_now_add=False)

class Notification(User):
    date_created = ndb.DateProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    is_read = ndb.BooleanProperty(default=False, indexed=True)

class Circle(User):
    date_created = ndb.DateProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)

class Answer(Question):
    description = ndb.StringProperty(indexed=False)
    date_created = ndb.DateProperty(auto_now_add=True)
    email = ndb.StringProperty(indexed=True)

class Upvote(Answer):
    email = ndb.StringProperty(indexed=True)

class Favorite(Question):
    email = ndb.StringProperty(indexed=True)

class Share(Question):
    circle_name = ndb.StringProperty(indexed=False)

class Contact(User):
    email = ndb.StringProperty(indexed=True)
    circle_names = ndb.StringProperty(repeated=True, indexed=False)
