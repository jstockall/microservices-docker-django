from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

@python_2_unicode_compatible
class Booking():
    id = ""
    user = ""
    showtime = ""
    movies = []
    def __str__(self):
		return u'{} {}'.format(self.user, self.showtime)

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

@python_2_unicode_compatible
class User():
    id = ""
    name = ""
    lastname = ""
    def __str__(self):
		return u'{} {}'.format(self.name, self.lastname)
