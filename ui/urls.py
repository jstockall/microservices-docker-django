from django.conf.urls import url

from . import views

app_name = 'ui'
urlpatterns = [
    url(r'^$', views.MoviesView.as_view(), name='movies'),
    url(r'^movies$', views.MoviesView.as_view(), name='movies'),
    url(r'^movie/([0-9a-f]+)$', views.MovieView.as_view(), name='movie'),
    url(r'^movie/add/$', views.new_movie),

    url(r'^showtimes$', views.ShowtimesView.as_view(), name='showtimes'),
    url(r'^showtime/([0-9a-f]+)$', views.ShowtimeView.as_view(), name='showtime'),
    url(r'^showtime/add/$', views.new_showtime),

    url(r'^booking/([0-9a-f]+)$', views.BookingView.as_view(), name='booking'),
    url(r'^booking/add/$', views.new_booking),

    url(r'^user/([0-9a-f]+)$', views.UserView.as_view(), name='user'),

    url(r'^admin$', views.admin, name='admin'),
]
