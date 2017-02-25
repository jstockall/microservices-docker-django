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

@python_2_unicode_compatible
class Movie():
    id = ""
    title = ""
    director = ""
    rating = ""
    def __str__(self):
		return self.title

@python_2_unicode_compatible
class ShowTime():
    id = ""
    date = ""
    createdon = ""
    movies = []
    def __str__(self):
		return self.date
    def tojson(self):
        raw = {}
        raw[u'id'] = self.id
        raw[u'date'] = self.date
        raw[u'createdon'] = self.createdon
        raw[u'movies'] = []
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
