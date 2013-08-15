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

    def startServer(self):
        try: 
        # We extract and store tweets in database and CSV file. Positive tweets
        # are stored in a database, while negative tweets are stored in CSV.
        # The CSV file is inspected in future for building corpus to use to 
        # build better classifier.
            print "Loading and Initializing Model, Connecting to Twitter...."

            patterns_nb = NB2()
            patterns_svm = SVMLearner()

            stream_corpus_table_nb = Datasheet.load("corpora/twitter/tweets_stream_data_nb.csv")
            index_corp_nb = dict.fromkeys(stream_corpus_table_nb.columns[0], True)

            stream_corpus_table_svm = Datasheet.load("corpora/twitter/tweets_stream_data_svm.csv")
            index_corp_svm = dict.fromkeys(stream_corpus_table_svm.columns[0], True)

            stream_predict_table_nb = Datasheet.load("predictions/twitter/nb_twitter.csv")
            index_pred_nb = dict.fromkeys(stream_predict_table_nb.columns[0], True)

            stream_predict_table_svm = Datasheet.load("predictions/twitter/svm_twitter.csv")
            index_pred_svm = dict.fromkeys(stream_predict_table_svm.columns[0], True)

        except:
            stream_predict_table_nb = Datasheet()
            index_pred_nb = {}
            stream_corpus_table_svm = Datasheet()
            index_corp_svm = {}

            stream_predict_table_svm = Datasheet()
            index_pred_svm = {}
            stream_corpus_table_nb = Datasheet()
            index_corp_nb = {}

            print "Error Initialization Model of Loading Files or Connecting to Twitter...."
        try:
            ensemble_table = Datasheet.load("predictions/ensenmble/ensenmble.csv")
        except:
            ensemble_table = Datasheet()
        
        #twitter_api = Twitter(license=None,language="en")

        #Connection initiation to the twitter streaming API. The mentioned 
        #diseases are tracked on twitter.
        stream_api = Twitter().stream("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS")


        print "Model Loading and Initialization Completed. Connection Successful...."
        counter = 0

        while True:
            counter +=1 

        #for i in range(100):
            #print i
            # Poll Twitter to see if there are new tweets.
            stream_api.update()
  
            #Tokenizer to separate words in tweets.          
            tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')
            
            #Determination of positve/negative tweets.
            for twt in reversed(stream_api):
                print "----------------------------------------------------Instance = %s-----------------------------------------------------------------------------------------" % counter
                                
                langDetect = LangDetect()
                lang = langDetect.lang_detect(twt.text)
                
                print "Tweet: %s, Lang: %s" % (twt.text, lang)

                if ('en' in lang):

                    #model = NaiveBayes() ; Model undeployed in version 0.7 (ensemble version)
                    #classifier = model.buildModel() This line is no longer required in version 0.6
                    #label = model.classify(twt.text) #Discarding the old NB classifier.

                    #Deployment of Model Ensemble of SVM and NB
                    nb_label = patterns_nb.classify(twt.text)
                    svm_label = patterns_svm.classify(twt.text)

                    geolocation = LocationDetect()
                    
                    print "NB Label: %s" % nb_label
                    print "SVM Label: %s" % svm_label
                    print "Location:", geolocation.getTweeterLocation(twt.author)
                    
                    id = str(hash(twt.author + twt.text))

                    if "positive" in nb_label and "positive" in svm_label:

                        label = nb_label #setting the label of tweet.
                        ensemble_table.append([nb_label, twt.text, twt.date]) #Storing ensemble result in CSV format before database storage

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
                                
                                print "Geolocation for %s is (%s, %s)" % (place, lng, lat)
                                
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
                                tweet.location_string = location.name
                       
                        print 'Tweet Label: %s. Storing in database' % label
                        print 'Disease Named Entity: %s, Location Named Entity: %s ', tweet.disease_type, location

                        tweet.save()
                        
                        if len(stream_predict_table_nb) == 0 or id not in index_pred_nb:
                            stream_predict_table_nb.append([id, twt.author, twt.text, nb_label, twt.date])
                            index_pred_nb[id] = True

                        if len(stream_predict_table_svm) == 0 or id not in index_pred_svm:
                            stream_predict_table_svm.append([id, twt.author, twt.text, svm_label, twt.date])
                            index_pred_svm[id] = True

                    else:
                        print 'Tweet Labels: NB - %s, SVM - %s; Storing in tweet corpus' %  (nb_label, svm_label)

                        if len(stream_corpus_table_nb) == 0 or id not in index_corp_nb:
                            stream_corpus_table_nb.append([id, twt.author, twt.text, nb_label, twt.date])
                            index_corp_nb[id] = True
                            
                        if len(stream_corpus_table_svm) == 0 or id not in index_corp_svm:
                            stream_corpus_table_svm.append([id, twt.author, twt.text, svm_label, twt.date])
                            index_corp_svm[id] = True


            # Clear the buffer every so often.
            stream_api.clear()

            # Wait awhile between polls.
            #time.sleep(1)   

            ensemble_table.save("predictions/ensenmble/ensenmble.csv")
            stream_predict_table_nb.save("predictions/twitter/nb_twitter.csv") 
            stream_predict_table_svm.save("predictions/twitter/svm_twitter.csv")
            stream_corpus_table_nb.save("corpora/twitter/tweets_stream_data_nb.csv")
            stream_corpus_table_svm.save("corpora/twitter/tweets_stream_data_svm.csv")

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
