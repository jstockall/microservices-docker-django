"""project URL Configuration"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('ui.urls')),
    url(r'^ui/', include('ui.urls')),
]
