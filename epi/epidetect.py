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
from nltk.tokenize import RegexpTokenizer


import tweepy



class Evaluator:
    ''' This class is meant to hold method stubs and some utilities for 
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
        ''' This menthod perform location detection from documents supplied.
        '''
        
        ## We initiate geocode API connection to Google Geocode API.
        try:
            g = geocoders.GoogleV3()
            place, (lat, lng) = g.geocode(args[0], exactly_one = False)[0]
        except:
            #print "In detectLocation: No geocode for Location specified: %s" % args[0]
            return None
                
        return (lat, lng, place) or None

    
    def getTweeterLocation(self, *args, **kwargs):
        ''' This method determines the location of a tweeter.
        It uses the tweepy API for connection to Twitter to determine location.
        The location returned is an approximation to the tweet location
        '''
        auth = tweepy.OAuthHandler("KVuUoRpXhSToTasXX3bB3A", "7ckvovFEbJkNGwl1Lj7txH0dJp5UiCLTJDEYoCl8U")
        auth.set_access_token("14702590-KRTpR5VYzZMxblqtKSW7x1MvaPA4WdMj3v6crmVY", "Ky6f6TN6ad3SgUeL17kH9dg3zQPs21NQoSTGnMlYw")
        
        #Setting authentication parameters after the settings above
        twitterapi = tweepy.API(auth)
        user = twitterapi.get_user(args[0])
           
        if user.location:
            return user.location
        else:
            return None

    def extractLocation(self, *args, **kwargs):
        '''This is a supporting method to perform extraction of location.
        The method determines if a mention in a document is part of predefined 
        locations of interest.
        '''
       
        # We use tokenizer provided by NLTK to form a regex that splits a 
        # document into array of words.
        try: 
            tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')

            # A list of pre-defined countries. Storage in a database is necessary
            countries = ['Turkey', 'Iran', 'Russia', 'Pakistan', 'UAE', 'Saudi Arabia', 'Sudan', 'Somalia', 'China', 'Saudi']
            tokens = tokenizer.tokenize(args[0])

            for word in tokens:
                if (word in countries):
                   
                    if ('Saudi' in word):
                        word = word+" Arabia"
                    return word
        except UnicodeEncodeError:
            print "Unable to encode some character(s) in tweet"    

        return False

class LangDetect:
    ''' This class detects the language of a document using a likelihood 
        algorithm and NLTK tokenizer.
    '''
    
    def lang_detect(self, document):
        ''' This method detects the language of a document using a likelihood 
        algorithm and NLTK tokenizer.
    '''
        ratios = self.lang_likelihood(document)
        most_rated_language = max(ratios, key=ratios.get)
       
        return most_rated_language
    
    def lang_likelihood(self, document):
        ''' This method computes the language likelihood using algorithm 
        and tokenizer from NLTK.
    '''
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
    ''' This class translates document from given language to english for 
    further processing by the classification algorithm.
    '''
    def translate(self, *args):
        ''' This method translates documents supplied. Connects to Google 
        Translate API.
    '''
        translator = GoogleTranslator()
        
        translation = translator.translate(args[0], target='en', source=args[1])
        
        print "Translation of: %s is: %s" % (args[0], str(translation[0]['translatedText']))
        
        return str(translation[0]['translatedText'])
        

class DiseaseType:
    ''' This class implements helper method to support detection of the types
        of diseases contained in reports/documents.
        Due to the nature of the classifier deployed, the type of disease
        detected by the model can not be pre-determined. So a separate 
        algorithm to ascertain the diseases with which a report is 
        associated is necessary
    ''' 

    def typedetect(self, *args):
        ''' This method detects the types of diseases contained in document.
            Due to the nature of the classifier deployed, the type of disease
            detected by the model can not be pre-determined. So a separate 
            algorithm to ascertain the diseases with which a report is 
            associated is necessary
        ''' 

        tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')

        with open('epidetect.properties') as f:
            for line in f:
                if 'TrackedDiseases' in line:
                    diseases = line      
  
        #diseases = tokenizer.tokenize(diseases)
        
        diseases = ['flu', 'swine flu', 'west nile', 'tuberculosis', \
        'avian influenza', 'influenza', 'measles', 'intestinal', 'dengue', \
        'respiratory','albinism', 'coronavirus', 'polio', 'legionella', \
        'gastroenteric', 'h1n1', 'hepatitis', 'ebola', 'hendra', 'influenzavirus', \
        'meningitis', 'h7n9', 'sars', 'hiv', 'aids', 'polio']

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
            
            data_dump = Datasheet.load("corpora/twitter/datadump2.csv")
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
                
            data_dump.save("corpora/twitter/datadump2.csv")
        
        
    def loaddata(self):
        
        tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')
        data_dump = Datasheet.load("archive/datadump.csv")
        index = dict.fromkeys(data_dump[0], True)
        
        for line in data_dump:
            tweet = epi.models.Tweet()
            tweet.text = line [1]
            tweet.label = line [3]
            tweet.owner = line [2]

            tweet.disease_type = line [5]
            print "Line 8 is: ", line[8]
            
            place = line [8]
            tweet.tweet_time = line [7]
            
            if place:
                       
                location = epi.models.Location()
                location.name = place

                lt = epi.models.LocationType()
                lt.name = 'City'
                location.locationtype = lt
                location.level = 2

                location.save()
                
                tweet.location = location
                
                try:
                    tweet.location_string = place
                except:
                    print "Unicode Error"
                
            tweet.save()
            
        print "Table length: ", len(data_dump)

   
            
            
            
