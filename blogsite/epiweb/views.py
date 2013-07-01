from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from epi.models import Tweet
from django.views import generic

class IndexView(generic.ListView):
    template_name = 'epiweb/index.html'
    context_object_name = 'tweet'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future).
        """
        return Tweet.objects.get(
            pk=1
        )

class DetailView(generic.DetailView):
    model = Tweet
    template_name = 'epiweb/detail.html'

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Tweet.objects.all()