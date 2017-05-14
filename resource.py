#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
import datetime
import time

import webapp2
import jinja2

import datastore as ds
import uuid

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ResourceHandler(webapp2.RequestHandler):
    def get(self):
        #clean up
        q = "Select * from Reservation"
        all = ndb.gql(q).fetch()
        for a in all:
            if a.endTime < datetime.datetime.now():
                a.key.delete()

        template = JINJA_ENVIRONMENT.get_template('webapp/templates/resources.html')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        entities = ndb.gql("Select * from Resource").fetch()

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources': entities
        }
        self.response.write(template.render(template_values))

class ResourceDetailHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/resource_detail.html')
        user = users.get_current_user()

        id = self.request.get('id')
        query = "Select * from Resource where guid="+"'" + id + "'"
        entity = ndb.gql(query).get()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        q = "Select * from Reservation where resourceid=" + "'" + id + "'"
        result = ndb.gql(q).fetch()

        reservations = []
        current = []
        for r in result:
            if r.startTime < datetime.datetime.now() and r.endTime > datetime.datetime.now():
                current.append(r)
            elif r.startTime > datetime.datetime.now():
                reservations.append(r)



        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'name' : entity.name,
            'res':entity,
            'reservation': reservations,
            'current': current
        }

        self.response.write(template.render(template_values))


class AddResourceHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/addResources.html')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        self.response.write(template.render(template_values))
    def post(self):
        resource = ds.Resource()
        guid = uuid.uuid4().hex
        resource.guid = guid
        resource.name = self.request.get('name')
        resource.userid =users.get_current_user().user_id()
        resource.user = users.get_current_user().email()
        d = self.request.get('date')
        darr = d.split("/")
        date = datetime.datetime(int(darr[2]), int(darr[0]), int(darr[1]), 0, 0)
        resource.date = date

        st = self.request.get('start_time')
        starr=st.split(":")
        resource.startTime = datetime.datetime(int(darr[2]), int(darr[0]), int(darr[1]), int(starr[0]), int(starr[1]))

        et = self.request.get('end_time')
        etarr=et.split(":")
        resource.endTime = datetime.datetime(int(darr[2]), int(darr[0]), int(darr[1]), int(etarr[0]), int(etarr[1]))

        # resource.endTime = datetime.datetime.strptime(et, "%H:%M").time()

        tags = self.request.get('tags')
        if(tags != ''):
            tags_inputArr = tags.split(',')
            tags_arr = []
            for t in tags_inputArr:
                tg = ds.Tag(content=t)
                tags_arr.append(tg)

            resource.tags = tags_arr

        resource.put()
        # self.response.write(resource)
        time.sleep(0.1)
        self.redirect('/resources')



class EditResourceHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/EditResources.html')
        user = users.get_current_user()
        id = self.request.get('id')
        query = "Select * from Resource where guid=" + "'" + id + "'"
        entity = ndb.gql(query).get()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        tags = entity.tags
        tagstr=''
        for i in range(len(tags)):
            if i == (len(tags)-1):
                tagstr += tags[i].content
            else:
                tagstr += tags[i].content
                tagstr += ","

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            're' : entity,
            'prev_tags': tagstr,
            'name' : entity.name,
            'id': id
        }
        self.response.write(template.render(template_values))

    def post(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/EditResources.html')
        user = users.get_current_user()
        id = self.request.get('id')
        query = "Select * from Resource where guid=" + "'" + id + "'"
        resource = ndb.gql(query).get()
        d = self.request.get('date')
        darr = d.split("/")
        date = datetime.datetime(int(darr[2]), int(darr[0]), int(darr[1]), 0, 0)
        resource.date = date

        st = self.request.get('start_time')
        starr = st.split(":")
        resource.startTime = datetime.datetime(int(darr[2]), int(darr[0]), int(darr[1]), int(starr[0]), int(starr[1]))

        et = self.request.get('end_time')
        etarr = et.split(":")
        resource.endTime = datetime.datetime(int(darr[2]), int(darr[0]), int(darr[1]), int(etarr[0]), int(etarr[1]))

        # resource.endTime = datetime.datetime.strptime(et, "%H:%M").time()

        tags = self.request.get('tags')
        if (tags != ''):
            tags_inputArr = tags.split(',')
            tags_arr = []
            for t in tags_inputArr:
                tg = ds.Tag(content=t)
                tags_arr.append(tg)

            resource.tags = tags_arr

        resource.put()
        # self.response.write(resource)
        time.sleep(0.1)
        url='/resources/detail?id='+id
        self.redirect(url)



app = webapp2.WSGIApplication([
    ('/resources', ResourceHandler),
    ('/resources/detail', ResourceDetailHandler),
    ('/resources/add', AddResourceHandler),
    ('/resources/edit', EditResourceHandler)
], debug=True)
