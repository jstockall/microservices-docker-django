from django.test import SimpleTestCase
from .models import Movie, User

class ModelTestCase(SimpleTestCase):

    def test_construct_movie(self):
        """Build the movie from a dict"""
        data = {}
        data[u'id'] = 123
        data[u'title'] = "movie title"
        data[u'director'] = "movie director"
        data[u'rating'] = 9.2
        movie = Movie(data)
        self.assertEqual(movie.title, "movie title")
        self.assertEqual(movie.director, "movie director")
        self.assertEqual(movie.rating, 9.2)
        self.assertEqual(movie.id, 123)

    def test_construct_movie_partial(self):
        """Build the movie from a dict"""
        movie = Movie({u'id':123})
        self.assertEqual(movie.title, "")
        self.assertEqual(movie.director, "")
        self.assertEqual(movie.rating, -1)
        self.assertEqual(movie.id, 123)

    def test_construct_user(self):
        """Build the user from a dict"""
        data = {}
        data[u'id'] = 123
        data[u'name'] = "John"
        data[u'lastname'] = "Doe"
        user = User(data)
        self.assertEqual(user.name, "John")
        self.assertEqual(user.lastname, "Doe")
        self.assertEqual(user.id, 123)
