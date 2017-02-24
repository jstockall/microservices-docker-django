from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.cache import cache

import json
import httplib
import os
import platform

from .models import Movie, Booking, ShowTime, User

def get_url(model):
    suffix = os.environ.get('DOMAIN_SUFFIX')
    if suffix is None:
        suffix = ''
    url = '{}{}'.format(model, suffix)
    print "Connecting to", url
    return url

def get_remote_data(model, id):
    # Check the cache first
    cached = cache.get(id)
    if cached is None:
        #print "Cache miss: ", id

        # Connect to the specified endpoint
        conn = httplib.HTTPConnection(get_url(model))

        # Get a json response back
        conn.request("GET", '/{}/{}'.format(model, id), headers={'accept':'application/json'})
        response = conn.getresponse()

        # check that we either got a successful response (200) or a previously retrieved,
        # but still valid response (304)
        status = response.status
        if status == 200 or status == 304:
            body = json.loads(response.read())
            data = body[u'data']
            cache.set(id, data)
            return data
        else:
            print 'Error status code: {} loading {} with id {}'.format(status, model, id)
            return None
    else:
        #print "Cache hit: ", id
        return cached

def get_remote_data_list(model, query):
    path = '/{}{}'.format(model, query)
    print "Path", path

    # Check the cache first
    cached = cache.get(path)
    if cached is None:
        print "Cache miss: ", path

        # Connect to the specified endpoint
        conn = httplib.HTTPConnection(get_url(model))

        # Get a json response back
        conn.request("GET", path, headers={'accept':'application/json'})
        response = conn.getresponse()

        # check that we either got a successful response (200) or a previously retrieved,
        # but still valid response (304)
        status = response.status
        if status == 200 or status == 304:
            # Return a dict out of the json response
            body = json.loads(response.read())
            data = body[u'data']
            cache.set(path, data)
            return data
        else:
            print 'Error status code: {} loading {} with id {}'.format(status, model, id)
            return None
    else:
        print "Cache hit: ", path
        return cached

def create_new(model, post_data):
    conn = httplib.HTTPConnection(get_url(model))
    conn.request("POST", '/{}'.format(model), body=json.dumps(post_data), headers={'Content-Type':'application/json'})
    response = conn.getresponse()

    # check that we either got a successful response (200)
    status = response.status
    if status == 200:
        body = json.loads(response.read())
        return body[u'data']
    else:
        print 'Error status code: {} creating new {}'.format(status, model)
        return None

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

def get_booking(id):
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


class MoviesView(generic.ListView):
    template_name = 'ui/movies.html'
    context_object_name = 'movie_list'

    def get_queryset(self):
        # Retrieve all from the movies endpoint
        movieData = get_remote_data_list("movies", "")

        if movieData is None:
            print 'Retrieved empty data from /movies'
            return None

        print movieData

        movies = []
        for m in movieData:
            movie = Movie()
            movie.id = m[u'id']
            movie.title = m[u'title']
            movie.director = m[u'director']
            movie.rating = m[u'rating']
            movies.append(movie)

        # sort the movie based on the title
        movies = sorted(movies, key=lambda b: b.title)
        return movies

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MoviesView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['hostname'] = platform.node()
        return context

class ShowtimesView(generic.ListView):
    template_name = 'ui/showtimes.html'
    context_object_name = 'showtime_list'

    def get_queryset(self):
        # Retrieve all from the showtimes endpoint
        showtimeData = get_remote_data_list("showtimes", "")

        if showtimeData is None:
            print 'Retrieved empty data from /showtimes'
            return None

        print showtimeData

        showtimes = []
        for s in showtimeData:
            showtime = ShowTime()
            showtime.id = s[u'id']
            showtime.date = s[u'date']
            showtime.createdon = s[u'createdon']
            showtime.movies = get_movies(s[u'movies'])
            showtimes.append(showtime)

        # sort the movie based on the date
        showtimes = sorted(showtimes, key=lambda b: b.date)
        return showtimes

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ShowtimesView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['hostname'] = platform.node()
        return context

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
        return get_booking(self.args[0])


class MovieView(generic.DetailView):
    context_object_name = 'movie'
    template_name = 'ui/movie.html'

    def get_object(self):
        return get_movie(self.args[0])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(generic.DetailView, self).get_context_data(**kwargs)

        # Retrieve all from the movies endpoint
        showtimes = get_remote_data_list("showtimes", "?movie=" + self.args[0])

        context['showtime_list'] = showtimes
        return context

def new_booking(request):
    if request.method == 'POST':

        firstname = request.POST[u'firstname']
        lastname = request.POST[u'lastname']
        showtimeId = request.POST[u'showtime']
        movieId = request.POST[u'movie']

        # See if we have a user that matches
        user = None

        # Create a new user
        post_data = {}
        post_data[u'data'] = {}
        post_data[u'data'][u'name'] = firstname
        post_data[u'data'][u'lastname'] = lastname

        response = create_new("users", post_data)
        if response is None:
            return HttpResponse('<h1>Error creating user</h1>')

        user = User(response)

        # Create a booking
        post_data[u'data'] = {}
        post_data[u'data'][u'userid'] = user.id
        post_data[u'data'][u'showtimeid'] = showtimeId
        post_data[u'data'][u'movies'] = []
        post_data[u'data'][u'movies'].append(movieId)

        response = create_new("bookings", post_data)
        if response is None:
            return HttpResponse('<h1>Error creating booking</h1>')

        booking = Booking()
        booking.id = response[u'id']
        booking.showtime = get_showtime(showtimeId)
        booking.user = user
        booking.movies = []
        booking.movies.append(get_movie(movieId))

        return render(request, 'ui/booking.html', {'booking': booking, 'hostname': platform.node()})
        #return HttpResponseRedirect("/booking/{}".format(booking.id))

    # if a GET (or any other method), return an error
    else:
         return HttpResponse('<h1>Method not supported</h1>')
