#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.web import SEARCH
from pattern.web import Google, Twitter, Facebook, Bing
from pygeocoder import Geocoder
from geopy import geocoders   
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords

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
            document = str(args[0])

            countries = ['Turkey', 'Iran', 'Russia', 'Pakistan', 'UAE', 'Saudi Arabia']
            documentsplit = document.split()

            for word in documentsplit:
                if (word in countries):
                    print "%s is extracted" % word
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
        
        if ('en' in most_rated_language):
            return True

        return False
    
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

