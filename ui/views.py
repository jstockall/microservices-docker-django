from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

import json
import httplib

from .models import Movie, Booking

class IndexView(generic.ListView):
    template_name = 'ui/index.html'
    context_object_name = 'booking_list'

    def get_queryset(self):
        """
        Call the webservice to get results
        TODO use redis to cache
        """
        # Connect to the bookings endpoint
        conn = httplib.HTTPConnection("bookings.dev")

        # Get a json response back
        conn.request("GET", "/bookings", headers={'accept':'application/json'})

        # check that we either got a successful response (200) or a previously retrieved,
        # but still valid response (304)
        resp = conn.getresponse()
        status = resp.status
        if status == 200 or status == 304:
            body = json.loads(resp.read())
            bookings = body[u'data']
            print bookings
            return bookings
        else:
            print 'Error status code: ', status
        return

class BookingView(generic.DetailView):
    context_object_name = 'booking'
    template_name = 'ui/booking.html'

    def get_remote_data(self, host, path):
        # Connect to the bookings endpoint
        conn = httplib.HTTPConnection(host)

        # Get a json response back
        conn.request("GET", path, headers={'accept':'application/json'})

        # check that we either got a successful response (200) or a previously retrieved,
        # but still valid response (304)
        resp = conn.getresponse()
        status = resp.status
        if status == 200 or status == 304:
            body = json.loads(resp.read())
            data = body[u'data']
            print data
            return data
        else:
            print 'Error status code: ', status
        return

    def get_object(self):
        id = self.args[0]


        booking = Booking()
        booking.id = id
        booking.movies = []

        # Load the booking
        bookingJson = self.get_remote_data("bookings.dev", "/bookings/" + id)

        # Load the showtimes
        showtimeJson = self.get_remote_data("showtimes.dev", "/showtimes/" + bookingJson[u'showtimeid'])
        if showtimeJson is not None:
            #print "showtime: " + showtimeJson
            booking.showtime = "get from json"
        else:
            booking.showtime = "Unable to load, see logs"

        # Load the user
        userJson = self.get_remote_data("users.dev", "/users/" + bookingJson[u'userid'])
        if userJson is not None:
            #print "user: " + str(userJson)
            booking.user = u'{} {}'.format(userJson[u'name'], userJson[u'lastname'])

        # Load the movies
        movieIds = bookingJson[u'movies']
        for movieId in movieIds:
            movieJson = self.get_remote_data("movies.dev", "/movies/" + movieId)
            movie = Movie()
            movie.id = movieId
            booking.movies.append(movie)
            if movieJson is not None:
                movie.title = movieJson[u'title']
                movie.rating = movieJson[u'rating']
                movie.createdon = movieJson[u'createdon']
            else:
                movie.title = "Unable to load, see logs"


        return booking




class MovieView(generic.DetailView):
    model = Movie
    template_name = 'ui/movie.html'

    def get_queryset(self):
        """

        """
        movie = Movie()
        return movie
