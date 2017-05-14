#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2
import datastore as ds
import datetime, uuid, time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ReservationHandler(webapp2.RequestHandler):
    def get(self):
        #clean up
        q = "Select * from Reservation"
        all = ndb.gql(q).fetch()
        for a in all:
            if a.endTime < datetime.datetime.now():
                a.key.delete()
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/reservations.html')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        entities = ndb.gql("Select * from Reservation").fetch()

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'reservation': entities
        }


        self.response.write(template.render(template_values))

class AddReservationHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/addReservation.html')
        user = users.get_current_user()
        id = self.request.get('id')

        query = "Select * from Resource where guid=" + "'" + id + "'"
        resource = ndb.gql(query).get()
        name = resource.name

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'name': name,
            'id': id
        }
        self.response.write(template.render(template_values))
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('webapp/templates/addReservation.html')
        id = self.request.get('id')
        query = "Select * from Resource where guid=" + "'" + id + "'"
        resource = ndb.gql(query).get()
        name = resource.name
        date = resource.date

        guid = uuid.uuid4().hex
        # resource.guid = guid

        reservation = ds.Reservation()
        reservation.guid = guid
        reservation.userid = users.get_current_user().user_id()
        reservation.ownerid = resource.userid
        reservation.resourceName = resource.name
        reservation.resourceid = id
        reservation.date = resource.date
        reservation.user = users.get_current_user().email()
        st = self.request.get('start_time')
        starr=st.split(":")
        timeS = datetime.time(int(starr[0]), int(starr[1]))
        startTime = datetime.datetime.combine(date.date(), timeS)

        error = False
        err = ""
        if(startTime < resource.startTime):
            error = True
            err = "Start time earlier than available time!"
        else:
            duration = int(self.request.get('duration'))
            est_endtime = startTime + datetime.timedelta(minutes = duration)
            if (est_endtime > resource.endTime):
               error = True
               err = "End time later than available time!"

        q = "Select * from Reservation where resourceid=" + "'" + id + "'"
        past_re = ndb.gql(q).fetch()
        for r in past_re:
            if (r.startTime <= startTime and r.endTime > startTime and r.endTime <= est_endtime): #overlapped
                error = True
                err = "This time slot is booked by someone else"
            elif (r.startTime > startTime and r.endTime < est_endtime): #in middle
                error = True
                err = "This time slot is booked by someone else"
            elif (r.startTime > startTime and r.startTime < est_endtime and r.endTime > est_endtime): #in middle
                error = True
                err = "This time slot is booked by someone else"
            elif (r.startTime < startTime and r.endTime > est_endtime):
                error = True
                err = "This time slot is booked by someone else"


        if error:
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
                'url_linktext': url_linktext,
                'name': name,
                'id': id,
                'error': err
            }
            self.response.write(template.render(template_values))
        else:
            reservation.startTime = startTime
            reservation.duration = duration
            reservation.endTime = est_endtime
            resource.lastRed = datetime.datetime.now()
            resource.put()
            reservation.put()
            time.sleep(0.1)
            self.redirect('/reservations')

class DeleteReservationHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get('id')
        user = users.get_current_user()

        query = "Select * from Reservation where guid=" + "'" + id + "'"
        r = ndb.gql(query).get()
        r.key.delete()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }
        referrer = self.request.headers.get('referer')
        if referrer:
            return self.redirect(referrer)
        return self.redirect_to('/')

app = webapp2.WSGIApplication([
    ('/reservations', ReservationHandler),
    ('/reservations/add', AddReservationHandler),
    ('/reservations/delete', DeleteReservationHandler)
], debug=True)