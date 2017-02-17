from __future__ import unicode_literals

from django.db import models
import datetime


class Booking():
    id = -1
    user = ""
    showtime = ""
    movies = []

class Movie():
    id = -1
    title = ""
    director = ""
    rating = ""
