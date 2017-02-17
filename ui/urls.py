from django.conf.urls import url

from . import views

app_name = 'ui'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^booking/([0-9a-f]+)$', views.BookingView.as_view(), name='booking'),
    url(r'^movie/([0-9a-f]+)$', views.MovieView.as_view(), name='movie'),
]