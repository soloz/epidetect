#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os, sys; sys.path.insert(0, os.path.join("..", ".."))
from pattern.web import SEARCH
from pattern.web import Google, Twitter, Facebook, Bing, hashtags 
from pattern.db  import Datasheet, pprint
from pattern.search import taxonomy, search
from pattern.en import parsetree
from classification import *
from epi.epidetect import *

import json

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
            for tweet in reversed(stream_api):
                print "Tweet is %s" % tweet.text
                
                lang = LangDetect()

                if (lang.lang_detect(tweet.text)):
                    model = NaiveBayes()
                    classifier = model.buildModel()
                    label = model.classify(tweet.text, classifier)
                    
                    print "Label of tweet is %s" % label
                    
                    geolocation = LocationDetect()
                    country = geolocation.extractLocation(tweet.text)

                id = str(hash(tweet.author + tweet.text))

                if len(stream_table) == 0 or id not in index:
                    stream_table.append([id, tweet.author, tweet.text, tweet.url, hashtags(tweet.text), tweet.date, tweet.language])
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
