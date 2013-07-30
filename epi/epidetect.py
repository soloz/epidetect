#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.web import SEARCH
from pattern.web import Google, Twitter, Facebook, Bing
from pygeocoder import Geocoder
from geopy import geocoders   
from geopy.geocoders import *
from nltk import wordpunct_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from pretests.gtranslate import *
from pattern.db  import Datasheet
import epi.models

import tweepy



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
        
        try:
            g = geocoders.GoogleV3()
            place, (lat, lng) = g.geocode(args[0], exactly_one = False)[0]
        except:
            #print "In detectLocation: No geocode for Location specified: %s" % args[0]
            return None
                
        return (lat, lng, place) or None

    
    def getTweeterLocation(self, *args, **kwargs):
        ''' Perform location detection from tweets.
        '''
        auth = tweepy.OAuthHandler("KVuUoRpXhSToTasXX3bB3A", "7ckvovFEbJkNGwl1Lj7txH0dJp5UiCLTJDEYoCl8U")
        auth.set_access_token("14702590-KRTpR5VYzZMxblqtKSW7x1MvaPA4WdMj3v6crmVY", "Ky6f6TN6ad3SgUeL17kH9dg3zQPs21NQoSTGnMlYw")
        
        twitterapi = tweepy.API(auth)
        user = twitterapi.get_user(args[0])
           
        if user.location:
            return user.location
        else:
            return None

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
        
class Utility:
    ''' Utility class to handle issues such as database consolidation
        and data migration.
    ''' 
    
    def dumpdata(self):
        ''' Utility method to dump data in a csv file for later upload to the
        final database. Final database fields is found below.
        ---------------------------------------------------------------------
            1.) text = models.CharField(max_length=200)
            2.) owner = models.CharField(max_length=20)
            3.) label = models.CharField(max_length=20)
            4.) usage = models.CharField(max_length=20)
            5.) disease_type = models.CharField(max_length=20, null=True)
            6.) urlentity = models.CharField(max_length=20)
            7.) hashtagentity = models.CharField(max_length=20)
            8.) tweet_time = models.DateTimeField(db_index=True, default=datetime.now)
            9.) location= models.ForeignKey(Location, null=True, blank=True)
            10.) location_string = models.CharField(max_length=20, null=True)
            11.) from_lang = models.CharField(max_length=20)
            12.) lat
            13.) lng
            14.) country
            
        ''' 
        try: 
        # We extract information from database and store in a csv
            
            data_dump = Datasheet.load("archive/database/datadump.csv")
            index = dict.fromkeys(data_dump[0], True)

        except:
            data_dump = Datasheet()
            index = {}
        
        for tweet in epi.models.Tweet.objects.all(): 
            id = str(hash(tweet.owner + tweet.text))   
            
            if len(data_dump) == 0 or id not in index:
                data_dump.append([id, tweet.text, tweet.owner, tweet.label, \
                tweet.usage, '', tweet.urlentity, tweet.tweet_time,\
                '', tweet.location, ''])
                index[id] = True
                
            data_dump.save("archive/database/datadump.csv")
        
        
    def loaddata(self):
        try: 
        # We extract information from database and store in a csv
            
            data_dump = Datasheet.load("archive/database/datadump.csv")
            index = dict.fromkeys(data_dump[0], True)

        except:
            data_dump = Datasheet()
            index = {}
            
            
            
