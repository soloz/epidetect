#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.web import SEARCH
from pattern.web import Google, Twitter, Facebook, Bing
from pygeocoder import Geocoder
from geopy import geocoders   
from nltk import wordpunct_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from pretests.gtranslate import *


class Evaluator:
    ''' This class holds method stubs and some utilities for 
        connecting to the GPHIN, WHO, and ProMED-Mail data sources for evaluation.
    '''
       
    def getGPHINData(self, *args, **kwargs):
        ''' Perform connection to GPHIN and get data.  This should 
            return False if everything passes, otherwise a list of 
            string representations of validation errors.
        '''
        pass

    def getWHOData(self, *args, **kwargs):
        ''' Perform connection to WHO Data sources and get data.  This should 
            return False if everything passes, otherwise a list of 
            string representations of validation errors.
        '''
        pass

    def getProMEDMailData(self, *args, **kwargs):
        ''' Perform connection to ProMEDMail Data source and get data.  This should 
            return False if everything passes, otherwise a list of 
            string representations of validation errors.
        '''
        pass

class Disambiquator:
    ''' This class holds method stubs and some utilities for 
        performing disambiquation.
    '''
       
    def disabiguate(self, *args, **kwargs):
        ''' Perform disambiquation on a given collection of documents.
        '''
        pass

class LocationDetect:
    ''' This class holds method stubs and some utilities for 
        performing geolocation, geocoding and geonaming of 
        locations.
    '''
      
    def detectLocation(self, *args, **kwargs):
        ''' Perform location detection from tweets.
        '''
        g = geocoders.GoogleV3()
        place, (lat, lng) = g.geocode(args[0])
        return (lat, lng)

    def extractLocation(self, *args, **kwargs):
        '''Performs extraction of Location information from Documents
        '''
       
        try: 
            tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')

            countries = ['Turkey', 'Iran', 'Russia', 'Pakistan', 'UAE', 'Saudi Arabia', 'Sudan', 'Somalia', 'China', 'Saudi']
            tokens = tokenizer.tokenize(args[0])

            for word in tokens:
                if (word in countries):
                    print "%s is extracted" % word
                    if ('Saudi' in word):
                        word = word+" Arabia"
                    return word
        except UnicodeEncodeError:
            print "Unable to encode some character(s) in tweet"    

        return False

class LangDetect:
    ''' This class detects the language of a document using a likelihood algorithm and NLTK tokenizer.
    '''
    
    def lang_detect(self, document):
        ratios = self.lang_likelihood(document)
        most_rated_language = max(ratios, key=ratios.get)
       
        return most_rated_language
    
    def lang_likelihood(self, document):
        languages_likelihood = {}

        tokens = wordpunct_tokenize(document)
        words = [word.lower() for word in tokens]

        for language in stopwords.fileids():
            stopwords_set = set(stopwords.words(language))
            words_set = set(words)
            common_elements = words_set.intersection(stopwords_set)

            languages_likelihood[language] = len(common_elements) # language "score"

        return languages_likelihood


class LangTranslate:
    ''' This class translates document from given language to english for classification.
    '''
    def translate(self, *args):
        translator = GoogleTransator()
        
        print "Translation of: %s is: %s" % (args[0], translator.translate(text=args[0], target='en', source=args[1]))
        

class DiseaseType:
    ''' This class detects the types of diseases contained in document.
        Due to the nature of the classifier deployed, the type of disease
        detected by the model can not be pre-determined. So a separate 
        algorithm to ascertain the diseases with which a report is 
        associated is necessary
    ''' 

    def typedetect(self, *args):

        tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')

        with open('epidetect.properties') as f:
            for line in f:
                if 'TrackedDiseases' in line:
                    diseases = line      
  
        #diseases = tokenizer.tokenize(diseases)
        
        diseases = ['flu', 'swine flu', 'west nile', 'tuberculosis', 'avian influenza', 'influenza', 'measles', 'intestinal', 'dengue', 'respiratory', \
        'albinism', 'coronavirus', 'polio', 'legionella', 'gastroenteric', 'h1n1', 'hepatitis', 'ebola', 'hendra', 'influenzavirus', 'meningitis', 'h7n9', 'sars', 'hiv', 'aids', 'polio']

        document = tokenizer.tokenize(args[0])
        
        document = [word.lower() for word in document]
        diseases = [disease_word.lower() for disease_word in diseases]

        detected_diseases = []

        for disease in diseases:
            if disease in document:
                detected_diseases.append(disease)

        return detected_diseases
