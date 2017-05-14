#!/usr/bin/env python

from google.appengine.api import users
from google.appengine.ext import ndb


#define classes for database store
class Tag(ndb.Model):
    content = ndb.StringProperty()

class Resource(ndb.Model):
    guid = ndb.StringProperty()
    name = ndb.StringProperty()
    userid = ndb.StringProperty()
    user = ndb.StringProperty()
    date = ndb.DateTimeProperty()
    startTime = ndb.DateTimeProperty()
    endTime = ndb.DateTimeProperty()
    postdate = ndb.DateTimeProperty(auto_now_add=True)
    tags = ndb.StructuredProperty(Tag, repeated=True)
    lastRed = ndb.DateTimeProperty()

class Reservation(ndb.Model):
    userid = ndb.StringProperty()
    user = ndb.StringProperty()
    guid = ndb.StringProperty()
    ownerid = ndb.StringProperty()
    resourceid = ndb.StringProperty()
    resourceName = ndb.StringProperty()
    date = ndb.DateTimeProperty()
    startTime = ndb.DateTimeProperty()
    duration = ndb.IntegerProperty()
    endTime = ndb.DateTimeProperty()
    postdate = ndb.DateTimeProperty(auto_now_add=True)
