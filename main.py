#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2

import datetime
import datastore

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


#define handlers for pages

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/index.html')
        user = users.get_current_user()

        #clean up
        q = "Select * from Reservation"
        all = ndb.gql(q).fetch()
        for a in all:
            if a.endTime < datetime.datetime.now():
                a.key.delete()

        reservation = []
        your_resources = []
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            query = "Select * from Reservation where userid=" + "'" + user.user_id() + "' ORDER BY startTime ASC"
            reservation = ndb.gql(query).fetch()

            u_resources = "Select * from Resource where userid=" + "'" + user.user_id() + "' ORDER BY lastRed DESC"
            your_resources = ndb.gql(u_resources).fetch()

        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        q_resources = "Select * from Resource ORDER BY lastRed DESC"
        resources = ndb.gql(q_resources).fetch()


        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'reservation': reservation,
            'resources': resources,
            'your_resources': your_resources
        }
        self.response.write(template.render(template_values))

class UserHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/user.html')
        id = self.request.get('id')
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            query = "Select * from Reservation where userid=" + "'" + id + "' ORDER BY startTime ASC"
            reservation = ndb.gql(query).fetch()

            u_resources = "Select * from Resource where userid=" + "'" + id + "' ORDER BY lastRed DESC"
            your_resources = ndb.gql(u_resources).fetch()

        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'reservation': reservation,
            'your_resources': your_resources
        }
        self.response.write(template.render(template_values))

class TagHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/tags.html')
        tag = self.request.get('tag')
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        q = "Select * from Resource ORDER BY lastRed DESC"
        all_res = ndb.gql(q).fetch()

        res = []
        for r in  all_res:
            for t in r.tags:
                if tag == t.content:
                    res.append(r)



        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources': res
        }
        self.response.write(template.render(template_values))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/user', UserHandler),
    ('/tag', TagHandler)
], debug=True)
