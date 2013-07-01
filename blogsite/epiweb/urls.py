from django.conf.urls import patterns, url

from epiweb import views

urlpatterns = patterns('',
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='details'),
)