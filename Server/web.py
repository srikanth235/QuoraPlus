
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


#from helpers import FunctionLoader, jinja2_template_loader
#from helpers import jinja2_environment
#from helpers import template_handler, json_handler

from model import *

class Main(webapp2.RequestHandler):
    #@template_handler('main.html')
    def get(self):
#         tables = Table.query().fetch(100)
#         return {
#             'tables': tables
#         }
          self.response.out.write("Hello, Welcome to Quora+")

######### Jinja Stuff ###########
# We use some hardcore caching, it's over in helpers.py

#Any variables that we want available in all templates
#jinja2_environment.globals.update({
#    'uri_for': webapp2.uri_for
#})


###### ROUTES and WSGI STUFF ######

url_routes = []
url_routes.append(
    routes.RedirectRoute(r'/',
                         handler=Main,
                         strict_slash=True,
                         name="main")
)
# url_routes.append(
#     routes.RedirectRoute(r'/new',
#                          handler=New,
#                          strict_slash=True,
#                          name="new")
# )
# url_routes.append(
#     routes.RedirectRoute(r'/table/<table_id:\d+>/',
#                          handler=Details,
#                          strict_slash=True,
#                          name="details")
# )
# url_routes.append(
#     routes.RedirectRoute(r'/table/<table_id:\d+>/result',
#                          handler=Result,
#                          strict_slash=True,
#                          name="result")
# )
# url_routes.append(
#     routes.RedirectRoute(r'/table/<table_id:\d+>/join',
#                          handler=Join,
#                          strict_slash=True,
#                          name="join")
# )
# url_routes.append(
#     routes.RedirectRoute(r'/table/<table_id:\d+>/resolve',
#                          handler=Resolve,
#                          strict_slash=True,
#                          name="resolve")
# )

app = webapp2.WSGIApplication(url_routes)
