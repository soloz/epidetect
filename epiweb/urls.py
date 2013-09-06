from django.conf.urls import patterns, url

from epiweb import views

urlpatterns = patterns('',
    url(r'^prototype$', views.formhandler, name='formhandler'),
    url(r'^(?P<disease>\w+)', views.ImprovedIndexView.as_view()),
    url(r'^performance$', views.performance, name='performance'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='details'),
)
