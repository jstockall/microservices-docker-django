from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
import json

@python_2_unicode_compatible
class Booking():
    id = None
    user = None
    showtime = None
    movie = None
    def __str__(self):
		return self.showtime
    def __init__(self, id=None):
        self.id = id

@python_2_unicode_compatible
class Movie():
    id = ""
    title = ""
    director = ""
    rating = ""
    def __str__(self):
		return self.title
    def __init__(self, dict={}):
        self.id = dict.get(u'id', "")
        self.title = dict.get(u'title', "")
        self.director = dict.get(u'director', "")
        self.rating = dict.get(u'rating', -1)

@python_2_unicode_compatible
class ShowTime():
    id = ""
    date = ""
    createdon = ""
    movies = []
    def __str__(self):
		return self.date
    def __init__(self, dict={}):
        self.id = dict.get(u'id', "")
        self.date = dict.get(u'date', "")
        self.createdon = dict.get(u'createdon', "")
    def tojson(self):
        raw = {u'id':self.id, u'date':self.date, u'createdon':self.createdon, u'movies':[]}
        for movie in self.movies:
            raw[u'movies'].append(movie.id)
        return raw


@python_2_unicode_compatible
class User():
    id = ""
    name = ""
    lastname = ""
    def __str__(self):
		return u'{} {}'.format(self.name, self.lastname)
    def __init__(self, dict):
        self.id = dict[u'id']
        self.name = dict[u'name']
        self.lastname = dict[u'lastname']
