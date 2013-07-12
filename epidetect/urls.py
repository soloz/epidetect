from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'blogsite.views.home', name='home'),
    # url(r'^blogsite/', include('blogsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^epiweb/', include('epiweb.urls', namespace="epiweb")),
    url(r'^epiweb/prototype', include('epiweb.urls', namespace="epiweb")),
    url(r'^epiweb/documentclass', include('epiweb.urls', namespace="epiweb")),
    url(r'^admin/', include(admin.site.urls)),
)
