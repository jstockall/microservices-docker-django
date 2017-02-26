from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.cache import cache

import json
import httplib
import os
import platform
import datetime

from .models import Movie, Booking, ShowTime, User

NEW_USER_ID = u'-- Create New User --'

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
        print "Cache miss: ", id

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
        print "Cache hit: ", id
        return cached

def get_remote_data_list(model, query=""):
    path = '/{}{}'.format(model, query)
    print "Path", path

    # Check the cache first
    cached = cache.get(path)
    if cached is None:
        print "Cache miss:", path

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
            if data is None:
                data = {}
            cache.set(path, data)

            print "Returning:", data
            return data
        else:
            print 'Error status code: {} loading {} with id {}'.format(status, model, id)
            return {}
    else:
        print "Cache hit: ", path
        return cached

def create_new(model, post_data):
    conn = httplib.HTTPConnection(get_url(model))
    conn.request("POST", '/{}'.format(model), body=json.dumps(post_data), headers={'Content-Type':'application/json','accept':'application/json'})
    response = conn.getresponse()

    # check that we either got a successful response (200)
    status = response.status
    if status == 200:
        body = json.loads(response.read())
        return body[u'data']
    else:
        print 'Error status code: {} creating new {}'.format(status, model)
        return None


def update(model, id, put_data):
    print "Updating {} id {} with data {}".format(model, id, put_data)

    conn = httplib.HTTPConnection(get_url(model))
    conn.request("PUT", '/{}/{}'.format(model, id), body=json.dumps(put_data), headers={'Content-Type':'application/json','accept':'application/json'})
    response = conn.getresponse()

    # check that we either got a successful response (200)
    status = response.status
    if status == 200:
        body = json.loads(response.read())
        return body[u'data']
    else:
        print 'Error status code: {} updating {}'.format(status, model)
        return None


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
    # Load the user
    userJson = get_remote_data("users", id)
    if userJson is not None:
        return User(userJson)
    else:
        raise ValueError("Unable to retrieve user: " + id)

def get_booking(id):
    booking = Booking()
    booking.id = id

    # Load the booking
    bookingJson = get_remote_data("bookings", id)

    # Load the showtimes
    booking.showtime = get_showtime(bookingJson[u'showtimeid'])

    # Load the user
    booking.user = get_user(bookingJson[u'userid'])

    # Load the movies
    booking.movie = get_movie(bookingJson[u'movieid'])

    return booking

#####################################
#
# Admin view
#
#####################################


def admin(request):

    # Retrieve all showtimes, movies and users
    return render(request, 'ui/admin.html', {
        'showtime_list': get_remote_data_list("showtimes"),
        'movie_list': get_remote_data_list("movies"),
        'user_list': get_remote_data_list("users"),
        'hostname': platform.node()})

#####################################
#
# Showtimes
#
#####################################

class ShowtimeView(generic.DetailView):
    context_object_name = 'showtime'
    template_name = 'ui/showtime.html'

    def get_object(self):
        return get_showtime(self.args[0])

class ShowtimesView(generic.ListView):
    template_name = 'ui/showtimes.html'
    context_object_name = 'showtime_list'

    def get_queryset(self):
        # Retrieve all from the showtimes endpoint
        showtimes = []
        for s in get_remote_data_list("showtimes"):
            showtime = ShowTime(s)
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

def new_showtime(request):
    if request.method == 'POST':
        print "new_showtime() request.POST", request.POST

        # Construct a new showtime document
        post_data = {}
        post_data[u'data'] = {}
        post_data[u'data'][u'date'] = request.POST[u'date']

        # Add the list of movie IDs to the showtime
        post_movies = request.POST.getlist(u'movies', [])
        print "movies from HTTP POST",post_movies

        post_data[u'data'][u'movies'] = []
        for m in post_movies:
            post_data[u'data'][u'movies'].append(m)

        print "new showtime",post_data

        response = create_new("showtimes", post_data)
        if response is None:
            raise Exception('Unable to create movie')

        showtime = ShowTime(response)
        for movie in response.get(u'movies', []):
            showtime.movies.append(get_movie(movie))

        cache.delete("/showtimes")
        cache.delete_pattern("/showtimes?movie=*")

        return render(request, 'ui/showtime.html', {'showtime': showtime, 'hostname': platform.node()})
    else:
        raise Exception('GET Method not supported on /showtimes/add')



#####################################
#
# Users
#
#####################################

class UserView(generic.DetailView):
    context_object_name = 'user'
    template_name = 'ui/user.html'

    def get_object(self):
        return get_user(self.args[0])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserView, self).get_context_data(**kwargs)

        # Retrieve all the bookings with this showtime and movie
        booking_list = []
        for b in get_remote_data_list("bookings", "?user=" + self.args[0]):
            booking_list.append(get_booking(b[u'id']))

        print "UserView booking_list=",booking_list

        # Add in the publisher
        context['hostname'] = platform.node()
        context['booking_list'] = booking_list
        return context


#####################################
#
# Movies
#
#####################################

def does_user_exst(users, userid):
    for u in users:
        #print "Matching userid {} in {}".format(userid, users)
        if u.id == userid:
            return True
    return False


class MovieView(generic.DetailView):
    context_object_name = 'movie'
    template_name = 'ui/movie.html'

    def get_object(self):
        return get_movie(self.args[0])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(generic.DetailView, self).get_context_data(**kwargs)

        # Retrieve all showtimes for the selected movie
        showtimes = get_remote_data_list("showtimes", "?movie=" + self.args[0])

        # Retrieve all the users so we can build the booking form
        users = get_remote_data_list("users")

        new_user = {}
        new_user[u'name'] = NEW_USER_ID
        new_user[u'id'] = NEW_USER_ID
        users.append(new_user)
        users = sorted(users, key=lambda b: b[u'name'])

        # Retrieve all the other users watching this booking
        other_users = []
        for b in get_remote_data_list("bookings", "?movie=" + self.args[0]):
            userId = b[u'userid']
            if not does_user_exst(other_users, userId):
                other_users.append(get_user(userId))

        print "MovieView.get_context_data(other_users={})".format(other_users)

        context['showtime_list'] = showtimes
        context['user_list'] = users
        context['other_user_list'] = other_users
        context['hostname'] = platform.node()
        return context

class MoviesView(generic.ListView):
    template_name = 'ui/movies.html'
    context_object_name = 'movie_list'

    def get_queryset(self):
        #Retrieve all from the movies endpoint
        movies = []
        for m in get_remote_data_list("movies"):
            movies.append(Movie(m))

        # sort the movie based on the title
        movies = sorted(movies, key=lambda b: b.rating, reverse=True)
        return movies

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MoviesView, self).get_context_data(**kwargs)

        # Add in the hostname of the UI container
        context['hostname'] = platform.node()
        return context


def new_movie(request):
    if request.method == 'POST':

        print "POST data", request.POST

        # Build a movie from the request.POST data
        post_data = {}
        post_data[u'data'] = {}
        post_data[u'data'][u'title'] = request.POST[u'title']
        post_data[u'data'][u'director'] = request.POST[u'director']
        post_data[u'data'][u'rating'] = float(request.POST[u'rating'])

        response = create_new("movies", post_data)
        if response is None:
            raise Exception('Unable to create movie')

        movie = Movie(response)
        showtimeIds = request.POST.getlist(u'showtimes', [])

        # For each showtime, update it's array of movies
        print "Request showtimes", showtimes
        showtime_list = []
        for showtimeId in showtimeIds:
            showtime = get_showtime(showtimeId)
            showtime.movies.append(movie)
            print "Updating showtime.movies to", showtime.movies
            update("showtimes", showtime.id, {u'data':showtime.tojson()})
            showtime_list.append(showtime)

        # Invalidate the cache for changed items
        cache.delete("/movies")
        cache.delete("/showtimes")

        return render(request, 'ui/movie.html', {'movie': movie, 'hostname': platform.node(), 'showtime_list': showtime_list})
    else:
        raise Exception('GET Method not supported on /movies/add')

def get_movie(id):
    movie = None

    movieJson = get_remote_data("movies", id)
    if movieJson is not None:
        movie = Movie(movieJson)
    else:
        movie = Movie({u'id':id})
        movie.title = "Unable to load, see logs"

    return movie

def get_movies(movieIds):

    movies = []
    # Load the movies
    for movieId in movieIds:
        movies.append(get_movie(movieId))
    return movies


#####################################
#
# Bookings
#
#####################################


class BookingView(generic.DetailView):
    context_object_name = 'booking'
    template_name = 'ui/booking.html'

    def get_object(self):
        return get_booking(self.args[0])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookingView, self).get_context_data(**kwargs)

        # Add in the hostname of the UI container
        context['hostname'] = platform.node()
        return context

def new_booking(request):
    if request.method == 'POST':

        # Read in the POST data
        showtimeId = request.POST[u'showtime']
        userId = request.POST.get(u'user', NEW_USER_ID)
        movieId = request.POST[u'movie']

        print "new_booking request request.POST", request.POST

        # Check for the special ID that indicates if we are creating a new user
        user = None
        if userId == NEW_USER_ID:
            # Build a http post based on the request
            post_data = {}
            post_data[u'data'] = {}
            post_data[u'data'][u'name'] = request.POST[u'name']
            post_data[u'data'][u'lastname'] = request.POST[u'lastname']

            print "new_booking post_data", post_data

            # Create the user on the users service
            response = create_new("users", post_data)
            if response is None:
                raise ValueError('Unable to create user')

            # Build a new user from the response
            user = User(response)

            print "Created new user from equest post data", user

            # Clear the cache
            cache.delete("/users")
        else:
            # Load existing user
            print "new_booking loading", userId
            user = get_user(userId)

        # Build a http post based on the request and the user
        post_data = {}
        post_data[u'data'] = {}
        post_data[u'data'][u'userid'] = user.id
        post_data[u'data'][u'showtimeid'] = showtimeId
        post_data[u'data'][u'movieid'] = movieId

        print "new_booking posting {} to {}".format(post_data, "/bookings")

        # Create the booking on the bookings service
        response = create_new("bookings", post_data)
        if response is None:
            raise ValueError('Unable to create booking')

        # Build a new booking from the response
        booking = Booking()
        booking.id = response[u'id']
        booking.showtime = get_showtime(showtimeId)
        booking.user = user
        booking.movie = get_movie(movieId)

        # Clear the cache
        cache.delete("/bookings")
        cache.delete_pattern("/bookings?movie="+movieId)

        return render(request, 'ui/booking.html', {'booking': booking, 'hostname': platform.node()})
    else:
        raise Exception('GET Method not supported on /bookings/add')
