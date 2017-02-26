from django.test import SimpleTestCase, Client
from .models import Movie, User, ShowTime

class ModelTestCase(SimpleTestCase):

    def test_construct_movie(self):
        """Build the movie from a dict"""
        movie = Movie({u'id':123, u'title':"movie title", u'director':"movie director", u'rating':9.2})
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
        user = User({u'id':123, u'name':"John", 'lastname':"Doe"})
        self.assertEqual(user.name, "John")
        self.assertEqual(user.lastname, "Doe")
        self.assertEqual(user.id, 123)

    def test_construct_showtime(self):
        """Build the showtime from a dict"""
        st = ShowTime({u'id':123, u'date':"2017-01-01", u'createdon':"abc123"})

        self.assertEqual(st.date, "2017-01-01")
        self.assertEqual(st.createdon, "abc123")
        self.assertEqual(st.id, 123)

    def test_showtime_tosjon(self):
        """Test the showtime json"""
        data = {u'id':123, u'date':"2017-01-01", u'createdon':"abc123", "movies":[]}
        st = ShowTime(data)

        self.assertEqual(st.tojson(), data)
