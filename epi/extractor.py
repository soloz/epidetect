#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os, sys; sys.path.insert(0, os.path.join("..", ".."))
from pattern.web import *
from pattern.db  import Datasheet, pprint
from pattern.search import taxonomy, search
from pattern.en import parsetree
from classification import *
from epi.epidetect import *
from epi.models import *
import pattern.web as webpatterns
from nltk.tokenize import RegexpTokenizer

import json, time


class TweetExtractor:
    ''' This class will extract tweets from Twitter via the Twitter search and streaming APIs. 
    The tweets would be stored in a CSV file for model building and subsequently into an SQL database '''

    def tweetSearch(self):
        try: 
        # We extract and store tweets in a Datasheet that can be saved as a CSV file.
        # The first column hold nique ID for each tweet. The CSV file is grown by adding new tweets that
        # haven not previously been encountered. An ID as index on the first column allows for checking if an ID already exists.
        # The index becomes important once more and more rows are added to the table (speed). 
        # The CSV is loaded into an SQLite database at some point.
            search_table = Datasheet.load("tweet_search_data.csv")
            index = dict.fromkeys(search_table.columns[0], True)
        except:
            search_table = Datasheet()
            index = {}

        twitter_api = Twitter(license=None,language="en")

        # With cached=False, a live request is sent to Twitter,
        # so we get the latest results for the query instead of those in the local cache.
        for tweet in twitter_api.search("flu", count=10000, cached=False):
            print tweet.text
            print tweet.author
            print tweet.date
            
            print hashtags(tweet.text) #print hastags associated with the tweet. 

            # a unique identifier for tweets is created by combining tweet content and author.
            id = str(hash(tweet.author + tweet.text))

            # Only non-existing tweets are added to the table.
            if len(search_table) == 0 or id not in index:
                print "Leng of search_table is %s" % len(search_table) 
                search_table.append([id, tweet.author, tweet.url, hashtags(tweet.text), tweet.country, tweet.speed, tweet.description, tweet.source, tweet.date, tweet.text])
                index[id] = True

        search_table.save("tweet_search_data.csv")

        print "Total results:", len(search_table)
        print


    def tweetStream(self):
        try: 
        # We extract and store tweets in a Datasheet that can be saved as a CSV file.
        # The first column hold nique ID for each tweet. The CSV file is grown by adding new tweets that
        # haven not previously been encountered. An ID as index on the first column allows for checking if an ID already exists.
        # The index becomes important once more and more rows are added to the table (speed). 
        # The CSV is loaded into an SQLite database at some point.
            
            stream_corpus_table = Datasheet.load("corpora/twitter/tweets_stream_data.csv")
            index_corp = dict.fromkeys(stream_corpus_table [0], True)

            stream_predict_table = Datasheet.load("predictions/NB/nb_twitter.csv")
            index_pred = dict.fromkeys(stream_predict_table.columns[0], True)

        except:
            stream_predict_table = Datasheet()
            index_pred = {}
            stream_corpus_table = Datasheet()
            index_corp = {}

        #twitter_api = Twitter(license=None,language="en")

        stream_api = Twitter().stream("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS")

        while True:
        #for i in range(100):
            #print i
            # Poll Twitter to see if there are new tweets.
            stream_api.update()
            # The stream is a list of buffered tweets so far,
            # with the latest tweet at the end of the list.
            
            tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')
            
            for twt in reversed(stream_api):
                                
                langDetect = LangDetect()
                lang = langDetect.lang_detect(twt.text)
                
                print "Tweet is %s, Lang = %s" % (twt.text, lang)

                if ('en' in lang):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(twt.text, classifier)

                    geolocation = LocationDetect()
                    
                    print "Label of tweet is %s" % label
                    print "Tweeter Location is", geolocation.getTweeterLocation(twt.author)
                    
                    id = str(hash(twt.author + twt.text))

                    if (label =='positive'):
                        tweet = Tweet()
                        tweet.text = twt.text
                        tweet.label = label
                        tweet.owner = twt.author
                        
                        diseasetype = DiseaseType()
                        diseases = diseasetype.typedetect(twt.text)

                        #country = geolocation.extractLocation(twt.text)
                        place = geolocation.getTweeterLocation(twt.author)
                        
                        if diseases:
                            if (len(diseases) > 1):
                                tweet.disease_type = ','.join(diseases)
                            else:
                                tweet.disease_type = diseases[0]
                                
                        if (place):
                            geolocationInfo = geolocation.detectLocation(place)
                            
                            if geolocationInfo:
                               
                                lat = "%.5f" % geolocationInfo[0]
                                lng = "%.5f" % geolocationInfo[1]
                                place = "%s" % geolocationInfo[2]
                                
                                print "Geolocation of %s is (%s, %s). Storing location information for document" % (place, lng, lat)
                                
                                location = Location()
                                location.name = place
                                location.latitude = lat
                                location.longitude = lng
                                
                                tokens = tokenizer.tokenize(place)
                                
                                if len(tokens) > 1:                            
                                    location.level = 2
                                    locationtype = LocationType.get_all_locationtypes()[1]
                                    
                                    parent_location = Location()
                                    parent_location.name = tokens[len(tokens) - 1]
                                    parent_location.level = 1
                                    parent_locationtype = LocationType.get_all_locationtypes()[0]
                                    parent_location.locationtype = parent_locationtype
                                    parent_location.save()
                                    location.parent = parent_location
                                                                        
                                else:
                                    location.level = 1
                                    locationtype = LocationType.get_all_locationtypes()[0]
             
                                location.locationtype = locationtype
                                
                                location.save()
                                tweet.location = location
                                tweet.location_string = str(location.name)
                       
                        print 'the tweet is %s, and storing in tweet database' % label
                        print 'the tweet categories are ', tweet.disease_type, diseases

                        tweet.save()
                        
                        if len(stream_predict_table) == 0 or id not in index_pred:
                            stream_predict_table.append([id, twt.author, twt.text, label, twt.date])
                            index_pred[id] = True

                    else:
                        print 'the tweet is negative, storing in tweet corpus'

                        if len(stream_corpus_table) == 0 or id not in index_corp:
                            stream_corpus_table.append([id, twt.author, twt.text, label, twt.date])
                            index_corp[id] = True


            # Clear the buffer every so often.
            stream_api.clear()

            # Wait awhile between polls.
            #time.sleep(1)   

            stream_predict_table.save("predictions/NB/nb_twitter.csv")
            stream_corpus_table.save("corpora/twitter/tweets_stream_data.csv")

        print "Total corpus results:", len(stream_corpus_table)
        print "Total predicted results:", len(stream_predict_table)
        print
        

class GoogleExtractor:
    ''' This class will extract search documents from Google via the Google search APIs. 
    The documents would be stored in a CSV file for model building and subsequently into an SQL database '''


    def googleSearch(self):
    
        engine = webpatterns.Google(license=None, language="en")
        
        q= "coronavirus"
        
        try: 
        # We extract and store Google documents in a Datasheet that can be saved as a CSV file.
        # The first column holds unique ID for each document. The CSV file is grown by adding new documents that
        # haven not previously been encountered. An ID as index on the first column allows for checking if an ID already exists.
        # The index becomes important once more and more rows are added to the table (performance). 
        # The CSV is loaded into an SQLite database at some point for future predictions.
        # It must be noted that the language of search outcomes in Google is somewhat different from the language used in tweets.

            google_corpus_table = Datasheet.load("corpora/google/google_corpus_data.csv")
            index_corp = dict.fromkeys(google_corpus_table.columns[0], True)

            google_predict_table = Datasheet.load("predictions/NB/nb_google.csv")
            index_pred = dict.fromkeys(google_predict_table.columns[0], True)
            
        except:
            google_corpus_table = Datasheet()
            index_corp = {}
            
            google_predict_table = Datasheet()
            index_pred = {}            

            
        for disease in ("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, \
            Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, \
            Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, \
            H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS"):

            taxonomy.append(disease, type="disease")

        p = "DISEASE" # Search pattern.

        for i in range(1,10):
            for result in engine.search(q, start=i, count=100, type=SEARCH):
                print plaintext(result.text) # plaintext() removes HTML formatting.
                print result.url
                print result.date
                print result.author
                print

                s = result.text
                
                print "Search result is : %s" % s
                s = plaintext(s)

                print "Document is %s" % s
              
                langDetect = LangDetect()
                lang = langDetect.lang_detect(s)
                                
                print "Document (and Language) is %s, Lang = %s" % (s, lang)

                if ('en' in lang):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(s, classifier)
                    
                    id = str(hash(label + plaintext(result.text)))
                    
                    print "Label of document is %s" % label
                    
                    if (label =='positive'):
                        googledoc = GoogleDocument()
                        googledoc.document = s
                        googledoc.label = label
                        #googledoc.search_time = result.date TODO: setup pytz to enable date from Google search.
                        
                        diseasetype = DiseaseType()
                        diseases = diseasetype.typedetect(s)
 
                        if diseases:
                            if (len(diseases) > 1):
                                googledoc.disease_type = ','.join(diseases)
                            else:
                                googledoc.disease_type = diseases[0]
                       
                        print 'The document is positive, storing in database'

                        geolocation = LocationDetect()
                        country = geolocation.extractLocation(s)

                        if (country):
                            print "Geolocation of %s is (%.5f, %.5f). Storing location information for document" % (country, geolocation.detectLocation(country)[0], geolocation.detectLocation(country)[1])
                            lat = "%.5f" % geolocation.detectLocation(country)[0]
                            lng = "%.5f" % geolocation.detectLocation(country)[1]
                            print (lat, lng)

                            locationtype = LocationType.get_all_locationtypes()[0]
                            location = Location()
                            location.name = country
                            location.latitude = lat
                            location.longitude = lng
                            
                            location.level = 1
                            location.locationtype = locationtype
                            location.save()
                            googledoc.location = location
                            googledoc.location_string = location.name                            
                        
                        print 'the document is %s, and storing in tweet database' % label
                        print 'the document categories are ', googledoc.disease_type, diseases
                        print 'the document location is ', googledoc.location_string
                        
                        googledoc.save()
                        
                                   
                        if len(google_predict_table) == 0 or id not in index_pred:
                            google_predict_table.append([id, label, plaintext(result.text), result.date])
                            index_pred[id] = True
                 
                    else:
                        print 'the document is negative, storing in tweet corpus'

                        if len(google_corpus_table) == 0 or id not in index_corp:
                            google_corpus_table.append([id, s, label, result.date])
                            index_corp[id] = True


            google_predict_table.save("predictions/NB/nb_google.csv")
            google_corpus_table.save("corpora/google/google_corpus_data.csv")

        print
        print len(google_corpus_table), "results from corpus table."
        print len(google_predict_table), "results from predictions table."

class BingExtractor:
    ''' This class will extract search documents from Bing via the Bing search APIs. 
    The documents would be stored in a CSV file for model building and subsequently into an SQL database '''

    def bingsearch(self):
        try: 
        # We extract and store Google documents in a Datasheet that can be saved as a CSV file.
        # The first column holds unique ID for each document. The CSV file is grown by adding new documents that
        # haven not previously been encountered. An ID as index on the first column allows for checking if an ID already exists.
        # The index becomes important once more and more rows are added to the table (performance). 
        # The CSV is loaded into an SQLite database at some point for future predictions.
        # It must be noted that the language of search outcomes in Google is somewhat different from the language used in tweets.

            bing_corpus_table = Datasheet.load("corpora/bing/bing_corpus_data.csv")
            index_corp = dict.fromkeys(google_corpus_table.columns[0], True)

            bing_predict_table = Datasheet.load("predictions/NB/nb_bing.csv")
            index_pred = dict.fromkeys(bing_predict_table.columns[0], True)
            
        except:
            bing_corpus_table = Datasheet()
            index_corp = {}
            
            bing_predict_table = Datasheet()
            index_pred = {}            


        q = 'coronavirus'         # Bing search query

        for disease in ("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, \
            Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, \
            Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, \
            H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS"):

            taxonomy.append(disease, type="disease")

        p = "DISEASE" # Search pattern.

        engine = Bing(license=None)

        for i in range(1): # max=10
            for result in engine.search(q, start=1, count=100, type=SEARCH, timeout=10):

                s = result.description
                
                print "Search result is : %s" % s
                s = plaintext(s)

                print "Document is %s" % s
                
                langDetect = LangDetect()
                lang = langDetect.lang_detect(s)
                                
                print "Document (and Language) is %s, Lang = %s" % (s, lang)

                if ('en' in lang):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(s, classifier)
                    
                    id = str(hash(label + s)) 
                    
                    print "Label of tweet is %s" % label
                    if (label =='positive'):
                        bingdoc = BingDocument()
                        bingdoc.document = s
                        bingdoc.label = label
                        bingdoc.save()
                        
                        diseasetype = DiseaseType()
                        diseases = diseasetype.typedetect(s)
 
                        if diseases:
                            if (len(diseases) > 1):
                                googledoc.disease_type = ','.join(diseases)
                            else:
                                googledoc.disease_type = diseases[0]
                       
                        print 'The document is positive, storing in database'

                        geolocation = LocationDetect()
                        country = geolocation.extractLocation(s)
                    
                        if (country):
                            print "Geolocation of %s is (%.5f, %.5f). Storing location information for document" % (country, geolocation.detectLocation(country)[0], geolocation.detectLocation(country)[1])
                            lat = "%.5f" % geolocation.detectLocation(country)[0]
                            lng = "%.5f" % geolocation.detectLocation(country)[1]
                            print (lat, lng)

                            locationtype = LocationType.get_all_locationtypes()[0]
                            location = Location()
                            location.name = country
                            location.latitude = lat
                            location.longitude = lng
                            location.level = 1
                            location.locationtype = locationtype
                            location.save()
                            bingdoc.location = location
                            bingdoc.location_string = location.name                            
                        
                        bingdoc.save()
                                   
                        if len(bing_predict_table) == 0 or id not in index_pred:
                            bing_predict_table.append([id, label, s, result.date])
                            index_pred[id] = True
                 
                    else:
                        print 'the document is negative, storing in tweet corpus'

                        if len(bing_corpus_table) == 0 or id not in index_corp:
                            bing_corpus_table.append([id, s, label, result.date])
                            index_corp[id] = True

            bing_predict_table.save("predictions/NB/nb_bing.csv")
            bing_corpus_table.save("corpora/google/bing_corpus_data.csv")

        print
        print len(bing_corpus_table), "results from corpus table."
        print len(bing_predict_table), "results from predictions table."
