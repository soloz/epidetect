from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from epi.models import *
from django.views import generic
from epiweb.prototypeform import ClassifyDocument
from epi.classification import NaiveBayes
from epi.epidetect import *
from time import time as taim
import json

class IndexView(generic.ListView):
    template_name = 'epiweb/index.html'
    context_object_name = 'data'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future).
        """
	data = Tweet.aggregate_by_day()
	jsondata = json.dumps(data)
	
        return data

class DetailView(generic.DetailView):
    model = Tweet
    template_name = 'epiweb/detail.html'

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Tweet.objects.all()

def formhandler(request):
    if request.method == 'POST': # If the form has been POSTed, request.method contains appropriate POST value...
        form = ClassifyDocument(request.POST) # Bind the Classify Document Form to the POSTed data

        if form.is_valid(): # All validation rules pass
            # Process the classify document form data in form.cleaned_data
            document = form.cleaned_data['text']
            #user = form.cleaned_data['userid']
            outcome = document

            model = NaiveBayes()
            classifier = model.buildModel()
            outcome = model.classify(document, classifier)
            
            geolocation = LocationDetect()
            country = geolocation.extractLocation(document)

            if (country):
                print "Geolocaiton of %s is (%.5f, %.5f). Storing location information for document" % (country, geolocation.detectLocation(country)[0], geolocation.detectLocation(country)[1])
		lat = "%.6f" % geolocation.detectLocation(country)[0]
		lng = "%.6f" % geolocation.detectLocation(country)[1]

		locationtype = LocationType.get_all_locationtypes()[0]
		location = Location()
		location.name = country
		location.latitude = lat
		location.longitude = lng
		location.level = 1
		location.locationtype = locationtype
		location.save()

            return render(request, 'epiweb/classify.html', {
                'outcome':outcome
            }) # Redirect after POST to appropriate method to display documetn class
        else:
            print "Submitted form is Invalid. Please verify that all fields are completed"

    else:
        form = ClassifyDocument() # Create an unbound Classify Document form

    return render(request, 'epiweb/classify.html', {
        'form': form,
    })

def documentclass(request):
    pass
