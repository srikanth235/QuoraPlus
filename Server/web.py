
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
import json
import os
import random
import webapp2

from jinja2 import Environment, FunctionLoader, MemcachedBytecodeCache

from webapp2_extras import routes

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb

from helpers import FunctionLoader, jinja2_template_loader
from helpers import jinja2_environment
from helpers import template_handler, json_handler

from model import Table, Participant

class Main(webapp2.RequestHandler):
    @template_handler('main.html')
    def get(self):
        tables = Table.query().fetch(100)
        return {
            'tables': tables
        }

class New(webapp2.RequestHandler):
    @template_handler('new.html')
    def get(self):
        return {}
    def post(self):
        #TODO consistency on the redirect
        name = self.request.get('name')
        
        if not name:
            return "You need to post the 'name' field"

        new_table = Table(name=name)
        new_table.put()

        self.redirect('/')

class Details(webapp2.RequestHandler):
    @template_handler('details.html')
    def get(self, table_id=None):
        if not table_id:
            return "You need to have a table_id"

        try:
            table = Table.get_by_id(int(table_id))
            if not table:
                raise Exception("No table retrieved")
        except Exception as e:
            logging.exception(e)
            return "invalid table_id specified"

        result = ""
        if table.hasResolved:
            for participant in table.users:
                if participant.user == users.get_current_user().email():
                    result = participant.result

        return {
            'name': table.name,
            'participants': table.users,
            'resolved': table.hasResolved,
            'table_id': table_id,
            'result': result
        }

class Result(webapp2.RequestHandler):
    @json_handler
    def get(self, table_id=None):
        if not table_id:
            return "You need to have a table_id"

        try:
            table = Table.get_by_id(int(table_id))
            if not table:
                raise Exception("No table retrieved")
        except Exception as e:
            logging.exception(e)
            return "invalid table_id specified"

        result = ""
        if table.hasResolved:
            for participant in table.users:
                if participant.user == users.get_current_user().email():
                    result = participant.result

        return result
        

class Resolve(webapp2.RequestHandler):
    def get(self, table_id=None):
        if not table_id:
            return "You need to have a table_id"

        try:
            table = Table.get_by_id(int(table_id))
            if not table:
                raise Exception("No table retrieved")
        except Exception as e:
            logging.exception(e)
            return "invalid table_id specified"

        @ndb.transactional
        def resolve(table_key):
            table = table_key.get()
            
            # First, calculate the total cost:
            cost = 0
            for participant in table.users:
                cost += participant.costOfMeal

            # and the tip
            tip = cost * 0.2
            total_cost = tip + cost
            

            generous_users = []
            # Next, see if anyone wants to pay for everything
            for participant in table.users:
                if participant.wantsToPayForEverything:
                    if participant.hasCredit or participant.cash >= cost:
                        generous_users.append(participant.user)

            if len(generous_users) >= 2:
                random.shuffle(generous_users)
                cost_payer = generous_users[0]
                tip_payer = generous_users[1]

                for participant in table.users:
                    if participant.user == cost_payer:
                        participant.result = "You pay for everyone's meal. It costs {}".format(
                            cost)
                    elif participant.user == tip_payer:
                        participant.result = "You pay the tip. It costs {}".format(
                            tip)
                    else:
                        participant.result = "You don't have to pay. Thanks, {} and {}!".format(
                            cost_payer,
                            tip_payer)

            elif len(generous_users) == 1:
                random.shuffle(generous_users)
                cost_payer = generous_users[0]

                for participant in table.users:
                    if participant.user == cost_payer:
                        participant.result = "You pay for everyone's meal and the tip. It costs {}".format(
                            total_cost)
                    else:
                        participant.result = "You don't have to pay. Thanks, {}!".format(
                            cost_payer)

            else:
                for participant in table.users:
                    if participant.cash > participant.costOfMeal:
                        participant.result = "You pay for your own meal with cash"
                    elif participant.hasCredit:
                        participant.result = "You pay for your own meal with credit"
                    else:
                        participant.result = "You're broke! You end up doing dishes all night."

            table.hasResolved = True
            table.put()

        resolve(table.key)
        self.redirect_to('details',table_id=table_id)

class Join(webapp2.RequestHandler):
    @template_handler('join.html')
    def get(self, table_id=None):
        if not table_id:
            return "You need to have a table_id"

        try:
            table = Table.get_by_id(int(table_id))
            if not table:
                raise Exception("No table retrieved")
        except Exception as e:
            logging.exception(e)
            return "invalid table_id specified"

        if table.hasResolved:
            self.redirect_to('details',table_id=table_id)

        return {
            'name': table.name
        }
    def post(self, table_id=None):
        if not table_id:
            self.response.write("You need to have a table_id")
            return

        try:
            table = Table.get_by_id(int(table_id))
            if not table:
                raise Exception("No table retrieved")
        except Exception as e:
            logging.exception(e)
            self.response.write("invalid table_id specified")
            return 

        cash = int(self.request.get("cash", None))
        credit = self.request.get("credit", None)
        everything = self.request.get("everything", None)
        cost = int(self.request.get("cost", None))

        if not cash:
            self.response.write("You must specify how much cash you have")
            return 

        if not cost:
            self.response.write("You must specify how much your meal costed")
            return 

        @ndb.transactional
        def add_participant(table_key, cash, credit, everything, cost):
            table = table_key.get()
            table.users.append(Participant(
                user=users.get_current_user().email(),
                cash=cash,
                hasCredit=True if credit else False,
                wantsToPayForEverything=True if everything else False,
                costOfMeal=cost,
                result=""))
            table.put()

        add_participant(table.key, cash, credit, everything, cost)
                
        self.redirect_to('details',table_id=table_id)
    

######### Jinja Stuff ###########
# We use some hardcore caching, it's over in helpers.py

#Any variables that we want available in all templates
jinja2_environment.globals.update({
    'uri_for': webapp2.uri_for
})


###### ROUTES and WSGI STUFF ######

url_routes = []
url_routes.append(
    routes.RedirectRoute(r'/',
                         handler=Main,
                         strict_slash=True,
                         name="main")
)
url_routes.append(
    routes.RedirectRoute(r'/new',
                         handler=New,
                         strict_slash=True,
                         name="new")
)
url_routes.append(
    routes.RedirectRoute(r'/table/<table_id:\d+>/',
                         handler=Details,
                         strict_slash=True,
                         name="details")
)
url_routes.append(
    routes.RedirectRoute(r'/table/<table_id:\d+>/result',
                         handler=Result,
                         strict_slash=True,
                         name="result")
)
url_routes.append(
    routes.RedirectRoute(r'/table/<table_id:\d+>/join',
                         handler=Join,
                         strict_slash=True,
                         name="join")
)
url_routes.append(
    routes.RedirectRoute(r'/table/<table_id:\d+>/resolve',
                         handler=Resolve,
                         strict_slash=True,
                         name="resolve")
)



app = webapp2.WSGIApplication(url_routes)
