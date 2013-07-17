from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from epi.models import Tweet
from django.views import generic
from epiweb.prototypeform import ClassifyDocument
from epi.classification import NaiveBayes
from epi.epidetect import Geologic

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
            
            geologic = Geologic()
            country = geologic.extractLocation(document)

            if (country):
                print geologic.detectLocation(country)

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
