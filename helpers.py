#
# Copyright (c) 2013 Murph Finnicum.
#
# Permission is granted to use this code for any purpose except that
# you may not use any portion of it as part of a MP2 submission for
# CS498stk at UIUC.
#
# This code is provided by the author 'as is' and comes without any
# warranty (Express, limited, or otherwise). In no event shall the
# author be liable for any damages or liability arising from the use
# of this code.
#

import os
import json

from jinja2 import Environment, FunctionLoader, MemcachedBytecodeCache

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb

VERSION = os.environ['CURRENT_VERSION_ID']

def template_handler(template_name):
    def decorator_generator(function):
        def decoration(self, *args, **kwargs):
            template = jinja2_environment.get_template(template_name)

            context = function(self, *args, **kwargs)

            if isinstance(context, dict):
                context['user'] = users.get_current_user()
                content = template.render(context)
                self.response.write(template.render(context))
            else:
                self.response.write(context)
        
                
        return decoration
    return decorator_generator

def json_handler(function):
    def json_handler_wrapper(self, *args, **kwargs):
        self.response.headers['Content-Type'] = "application/json"

        ret = function(self, *args, **kwargs)

        self.response.out.write(
            json.dumps(ret))
    return json_handler_wrapper

#jinja cache as per http://appengine-cookbook.appspot.com/
def jinja2_template_loader(templatename):
    cur = os.path.join(os.path.dirname(__file__), '')
    templatepath = os.path.abspath(cur + templatename)
    template = memcache.get(templatepath + VERSION)
    if template is None:
        try:
            template = file(templatepath).read()
            memcache.set(templatepath + VERSION, template)
        except:
            template = None

    modify_time = os.path.getmtime(templatepath)

    def uptodatefunc():
        if modify_time != os.path.getmtime(templatepath):
            memcache.delete(templatepath + VERSION)
            return False
        else:
            return True
        
    return (template, templatepath, uptodatefunc)

class jinja_bytecode_cache():
    @classmethod
    def get(self,key):
        logging.info("Getting from bytecode cache")
        return memcache.get(key + VERSION)
    def set(self,key,value,time=None):
        logging.info("Setting to bytecode cache")
        return memcache.set(key + VERSION, value, time)

jinja2_environment = Environment(
    loader=FunctionLoader(jinja2_template_loader),
    bytecode_cache=MemcachedBytecodeCache(memcache),
)

