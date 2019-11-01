from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^interests$', views.interests),
    url(r'^logout$', views.logout),
    url(r'^login$', views.login),
    url(r'^videos$', views.getVideos),
    url(r'^interest-search$', views.interestSearch),
    url(r'^wall$', views.wall),

]
