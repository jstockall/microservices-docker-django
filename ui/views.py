from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

import json
import httplib

from .models import Movie, Booking, ShowTime, User

def get_data_from_response(response):
    # check that we either got a successful response (200) or a previously retrieved,
    # but still valid response (304)
    status = response.status
    if status == 200 or status == 304:
        body = json.loads(response.read())
        data = body[u'data']
        return data
    else:
        print 'Error status code: ', status
        return None
    return

def get_remote_data(model, id):
    # Connect to the bookings endpoint
    conn = httplib.HTTPConnection('{}.dev'.format(model))

    # Get a json response back
    conn.request("GET", '/{}/{}'.format(model, id), headers={'accept':'application/json'})
    data = get_data_from_response(conn.getresponse())
    return data

def get_movie(id):
    movie = Movie()
    movie.id = id

    movieJson = get_remote_data("movies", id)
    if movieJson is not None:
        movie.director = movieJson[u'director']
        movie.title = movieJson[u'title']
        movie.rating = movieJson[u'rating']
    else:
        movie.title = "Unable to load, see logs"

    return movie

def get_movies(movieIds):

    movies = []
    # Load the movies
    for movieId in movieIds:
        movies.append(get_movie(movieId))
    return movies

def get_showtime(id):
    showtime = ShowTime()
    showtime.id = id

    # Load the showtime
    showtimeJson = get_remote_data("showtimes", id)
    if showtimeJson is not None:
        showtime.date = showtimeJson[u'date']
        showtime.createdon = showtimeJson[u'createdon']

        # Load the movies
        showtime.movies = get_movies(showtimeJson[u'movies'])
    else:
        showtime.date = "Unable to load, see logs"



    return showtime

def get_user(id):
    user = User()
    user.id = id

    # Load the user
    userJson = get_remote_data("users", id)
    if userJson is not None:
        user.name = userJson[u'name']
        user.lastname = userJson[u'lastname']
    else:
        user.name = "Unable to load, see logs"

    return user

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
        data = get_data_from_response(conn.getresponse())
        return data

class UserView(generic.DetailView):
    context_object_name = 'user'
    template_name = 'ui/user.html'

    def get_object(self):
        return get_user(self.args[0])

class ShowtimeView(generic.DetailView):
    context_object_name = 'showtime'
    template_name = 'ui/showtime.html'

    def get_object(self):
        return get_showtime(self.args[0])


class BookingView(generic.DetailView):
    context_object_name = 'booking'
    template_name = 'ui/booking.html'

    def get_object(self):
        id = self.args[0]

        booking = Booking()
        booking.id = id
        booking.movies = []

        # Load the booking
        bookingJson = get_remote_data("bookings", id)

        # Load the showtimes
        booking.showtime = get_showtime(bookingJson[u'showtimeid'])

        # Load the user
        booking.user = get_user(bookingJson[u'userid'])

        # Load the movies
        booking.movies = get_movies(bookingJson[u'movies'])

        return booking


class MovieView(generic.DetailView):
    context_object_name = 'movie'
    template_name = 'ui/movie.html'

    def get_object(self):
        return get_movie(self.args[0])
