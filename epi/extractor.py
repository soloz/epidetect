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
            stream_table = Datasheet.load("tweets_stream_data.csv")
            index = dict.fromkeys(stream_table.columns[0], True)
        except:
            stream_table = Datasheet()
            index = {}

        #twitter_api = Twitter(license=None,language="en")

        stream_api = Twitter().stream("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS")

        while True:
        #for i in range(100):
            #print i
            # Poll Twitter to see if there are new tweets.
            stream_api.update()
            # The stream is a list of buffered tweets so far,
            # with the latest tweet at the end of the list.
            for twt in reversed(stream_api):
                print "Tweet is %s" % twt.text
                
                lang = LangDetect()

                if (lang.lang_detect(twt.text)):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(twt.text, classifier)
                    
                    if (label =='positive'):
                        tweet = Tweet()
                        tweet.text = twt.text
                        tweet.label = label
                        tweet.owner = twt.author
                        tweet.save()
                        print 'the tweet is positive, storing in tweet database'

                    print "Label of tweet is %s" % label
                    
                    geolocation = LocationDetect()
                    country = geolocation.extractLocation(twt.text)

                    if (country and ('positive' in label)):
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

                id = str(hash(twt.author + twt.text))

                if len(stream_table) == 0 or id not in index:
                    stream_table.append([id, twt.author, twt.text, twt.url, hashtags(twt.text), twt.date, twt.language])
                    index[id] = True

            # Clear the buffer every so often.
            stream_api.clear()
            # Wait awhile between polls.
            #time.sleep(1)   
            stream_table.save("tweets_stream_data.csv")

        print "Total results:", len(stream_table)
        print

        
    def csvBuilderFromSource(self):
        data = []
        with open('../../data/0001.json') as f:
            for line in f:
                data.append(json.loads(line))
        myfile = open('../../data/output.json')
        myfile.write(data)
        myfile.close()


    def csvBuilderFromEn(self):
        json_data=open('../../data/0001.json').read()
        data = json.loads(json_data)

        print data

class GoogleExtractor:
    ''' This class will extract search documents from Google via the Google search APIs. 
    The documents would be stored in a CSV file for model building and subsequently into an SQL database '''

    global engine 
    engine = Google(license=None, language="en")
    
    global q
    q= "coronavirus"

    def googleSearch(self):
        try: 
        # We extract and store Google documents in a Datasheet that can be saved as a CSV file.
        # The first column holds unique ID for each document. The CSV file is grown by adding new documents that
        # haven not previously been encountered. An ID as index on the first column allows for checking if an ID already exists.
        # The index becomes important once more and more rows are added to the table (performance). 
        # The CSV is loaded into an SQLite database at some point for future predictions.
        # It must be noted that the language of search outcomes in Google is somewhat different from the language used in tweets.

            google_search_table = Datasheet.load("corpora/google/google_search_data.csv")
            index = dict.fromkeys(google_search_table.columns[0], True)

        except:
            google_search_table = Datasheet()
            index = {}

        for disease in ("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, \
            Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, \
            Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, \
            H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS"):

            taxonomy.append(disease, type="disease")

        p = "DISEASE" # Search pattern.

        for i in range(1,2):
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
              
                lang = LangDetect()

                if (lang.lang_detect(s)):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(s, classifier)
                    
                    print "Label of tweet is %s" % label
                    if (label =='positive'):
                        googledoc = GoogleDocument()
                        googledoc.document = s
                        googledoc.label = label
                        googledoc.save()
                        print 'the tweet is positive, storing in database'

                    geolocation = LocationDetect()
                    country = geolocation.extractLocation(s)

                    if (country and ('positive' in label)):
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

                    id = str(hash(label + plaintext(result.text)))               
                    
                    if len(google_search_table) == 0 or id not in index:
                        google_search_table.append([id, label, plaintext(result.text), result.date])
                        index[id] = True

        google_search_table.save("corpora/google/google_search_data.csv")


        print
        print len(google_search_table), "results."

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

            bing_search_table = Datasheet.load("corpora/bing/bing_search_data.csv")
            index = dict.fromkeys(bing_search_table.columns[0], True)

        except:
            bing_search_table = Datasheet()
            index = {}

        q = 'coronavirus'         # Bing search query

        for disease in ("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, \
            Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, \
            Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, \
            H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS"):

            taxonomy.append(disease, type="disease")

        p = "DISEASE" # Search pattern.

        engine = Bing(license=None)

        for i in range(1): # max=10
            for result in engine.search(q, start=i+1, count=100, cached=True):

                s = result.description
                
                print "Search result is : %s" % s
                s = plaintext(s)

                print "Document is %s" % s
                
                lang = LangDetect()

                if (lang.lang_detect(s)):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(s, classifier)
                    
                    print "Label of tweet is %s" % label
                    if (label =='positive'):
                        bingdoc = BingDocument()
                        bingdoc.document = s
                        bingdoc.label = label
                        bingdoc.save()
                        print 'the tweet is positive, storing in database'

                    geolocation = LocationDetect()
                    country = geolocation.extractLocation(s)

                    if (country and ('positive' in label)):
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
        
                    id = str(hash(label + s))               
                    
                    if len(bing_search_table) == 0 or id not in index:
                        bing_search_table.append([id, label, s, result.date])
                        index[id] = True
        bing_search_table.save("corpora/bing/bing_search_data.csv")
        
        print
        print len(bing_search_table), "results."