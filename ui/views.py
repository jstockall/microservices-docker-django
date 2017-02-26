from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
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

def create(model, post_data):
    conn = httplib.HTTPConnection(get_url(model))
    conn.request("POST", '/{}'.format(model), body=json.dumps(post_data),
                        headers={'Content-Type':'application/json','accept':'application/json'})
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
    conn.request("PUT", '/{}/{}'.format(model, id), body=json.dumps(put_data),
                        headers={'Content-Type':'application/json','accept':'application/json'})
    response = conn.getresponse()

    # check that we got a successful response (200)
    status = response.status
    if status == 200:
        body = json.loads(response.read())
        return body[u'data']
    else:
        print 'Error status code: {} updating {}'.format(status, model)
        return None

def delete(model, id):
    print "Deleting {} id {}".format(model, id)

    conn = httplib.HTTPConnection(get_url(model))
    conn.request("DELETE", '/{}/{}'.format(model, id), headers={'Content-Type':'application/json','accept':'application/json'})
    response = conn.getresponse()

    # check that we got a successful response (200)
    status = response.status
    if status != 204:
        print 'Error status code: {} deleting {}'.format(status, model)

def remove(request, model, delete_showtimes=False):
    if request.method == 'POST':
        print "remove_{}() request.POST {}".format(model, request.POST)

        # Validate the POST data
        models = model + "s"
        to_remove = request.POST.getlist(models, [])
        if len(to_remove) == 0:
            return HttpResponseServerError("<h1>ERROR: {}s is empty</h1>".format(model));

        # Remove each of the selected model objects
        for tr in to_remove:
            # delete any bookings for this objects
            for booking in get_remote_data_list("bookings", "?{}id={}".format(model, tr)):
                delete("bookings", booking[u'id'])
            if delete_showtimes:
                # Update any showtimes that referenced the movie
                for showtime in get_remote_data_list("showtimes", "?movie={}".format(tr)):
                    print "Existing showtime.movies to", showtime[u'movies']
                    showtime[u'movies'].remove(tr)
                    print "Updating showtime.movies to", showtime[u'movies']
                    update("showtimes", showtime[u'id'], {u'data':showtime})
            # delete the objects
            delete(models, tr)

        # Clear the cache and return to the admin page
        cache.delete("/" + models)
        return HttpResponseRedirect("/admin")
    else:
        raise Exception("{} Method not supported on /{}/remove".format(request.method, model))


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

def get_showtime(id):
    # Load the showtime
    data = get_remote_data("showtimes", id)
    if data is not None:
        # Build the showtime with id, date and created on from the response
        showtime = ShowTime(data)
        # Build the movies from the ids in the data
        showtime.movies = get_movies(data[u'movies'])
        return showtime

    # Return a placeholder
    return ShowTime({u'id':id, u'date':"Unable to load showtime with id " + id})

def add_showtime(request):
    if request.method == 'POST':
        print "add_showtime() request.POST", request.POST

        # Validate the POST data
        date = request.POST[u'date']
        if len(date) == 0:
            return HttpResponseServerError("<h1>ERROR: Date is required</h1>");

        # Construct a new showtime document
        post_data = {u'data': {u'date': date}}

        # Add the list of movie IDs to the showtime
        post_movies = request.POST.getlist(u'movies', [])
        print "movies from HTTP POST",post_movies

        post_data[u'data'][u'movies'] = []
        for m in post_movies:
            post_data[u'data'][u'movies'].append(m)

        print "new showtime",post_data

        response = create("showtimes", post_data)
        if response is None:
            return HttpResponseServerError("Unable to create showtime<br>" + post_data)

        showtime = ShowTime(response)
        for movie in response.get(u'movies', []):
            showtime.movies.append(get_movie(movie))

        cache.delete("/showtimes")
        cache.delete_pattern("/showtimes?movie=*")

        return render(request, 'ui/showtime.html', {'showtime':showtime, 'hostname':platform.node()})
    else:
        raise Exception(request.method + ' Method not supported on /showtime/add')

def remove_showtime(request):
    return remove(request, "showtime")

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

def get_user(id):
    # Load the user
    data = get_remote_data("users", id)
    if data is not None:
        return User(data)

    # Return a placeholder
    return User({u'id':id, u'name':"Unable to load user with id", u'lastname':id})

def does_user_exst(users, userid):
    for u in users:
        if u.id == userid:
            return True
    return False

def remove_user(request):
    return remove(request, "user")

#####################################
#
# Movies
#
#####################################

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

        # Add an option to create a new user
        new_user = {u'name':NEW_USER_ID, u'id':NEW_USER_ID}
        users.append(new_user)
        users = sorted(users, key=lambda b: b[u'name'])

        # Retrieve all the other users watching this booking
        other_users = []
        for b in get_remote_data_list("bookings", "?movie=" + self.args[0]):
            if not does_user_exst(other_users, b[u'userid']):
                other_users.append(get_user(b[u'userid']))

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


def add_movie(request):
    if request.method == 'POST':

        print "new_movie POST data", request.POST

        # Validate the POST data
        if len(request.POST[u'title']) == 0:
            return HttpResponseServerError("<h1>ERROR: Title is required</h1>");
        if len(request.POST[u'director']) == 0:
            return HttpResponseServerError("<h1>ERROR: Director is required</h1>");
        if len(request.POST[u'rating']) == 0:
            return HttpResponseServerError("<h1>ERROR: Rating is required</h1>");

        # Build a movie from the request.POST data
        post_data = {u'data': {u'title':request.POST[u'title'],
                               u'director':request.POST[u'director'],
                               u'rating':float(request.POST['rating'])}}

        response = create("movies", post_data)
        if response is None:
            return HttpResponseServerError("Unable to create movie<br>" + post_data)

        # Build a movie object for the view
        movie = Movie(response)

        # For each showtime, update it's array of movies
        # Build a list of showtimes for the view
        showtimeIds = request.POST.getlist(u'showtimes', [])
        print "Request showtime IDs", showtimeIds
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

        return render(request, 'ui/movie.html', {u'movie':movie,
                                                 u'hostname':platform.node(),
                                                 u'showtime_list':showtime_list})
    else:
        raise Exception('GET Method not supported on /movies/add')

def get_movie(id):
    data = get_remote_data("movies", id)
    if data is not None:
        return Movie(data)

    return Movie({u'id':id, u'title':"Unable to load movie with id " + id})

def get_movies(movieIds):
    movies = []
    for movieId in movieIds:
        movies.append(get_movie(movieId))
    return movies


def remove_movie(request):
    return remove(request, "movie", True)


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

def add_booking(request):
    if request.method == 'POST':

        # Validate the POST data
        if len(request.POST[u'showtime']) == 0:
            return HttpResponseServerError("<h1>ERROR: Showtime not selected</h1>");

        showtimeId = request.POST[u'showtime']
        userId = request.POST.get(u'user', NEW_USER_ID)
        movieId = request.POST[u'movie']

        print "add_booking request request.POST", request.POST

        # Check for the special ID that indicates if we are creating a new user
        user = None
        if userId == NEW_USER_ID:
            # Build a http post based on the request
            data = {u'data': {u'name': request.POST[u'name'],u'lastname': request.POST[u'lastname']}}

            print "add_user new user=", data

            # Create the user on the users service
            response = create("users", data)
            if response is None:
                raise ValueError('Unable to create user')

            # Build a new user object from the response
            user = User(response)

            print "Created new user", user

            # Clear the cache
            cache.delete("/users")
        else:
            # Load existing user
            print "add_booking loading", userId
            user = get_user(userId)

        # Build a http post based on the request and the user
        data = {u'data': {u'userid':user.id, u'showtimeid':showtimeId, u'movieid':movieId}}

        print "add_booking posting {} to {}".format(data, "/bookings")

        # Create the booking on the bookings service
        response = create("bookings", data)
        if response is None:
            raise ValueError('Unable to create booking')

        # Build a new booking from the response
        booking = Booking(response[u'id'])
        booking.showtime = get_showtime(showtimeId)
        booking.user = user
        booking.movie = get_movie(movieId)

        # Clear the cache
        cache.delete("/bookings")
        cache.delete_pattern("/bookings?movie="+movieId)
        cache.delete_pattern("/bookings?user="+user.id)

        return render(request, 'ui/booking.html', {'booking':booking, 'hostname':platform.node()})
    else:
        raise Exception('GET Method not supported on /bookings/add')

def get_booking(id):
    booking = Booking(id)

    # Load the booking
    data = get_remote_data("bookings", id)
    if data is not None:
        # Load the showtimes
        booking.showtime = get_showtime(data[u'showtimeid'])

        # Load the user
        booking.user = get_user(data[u'userid'])

        # Load the movie
        booking.movie = get_movie(data[u'movieid'])

    return booking
