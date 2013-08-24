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

            stream_corpus_table_svm = Datasheet.load("corpora/twitter/tweets_stream_data_svm.csv")
            index_corp_svm = dict.fromkeys(stream_corpus_table_svm.columns[0], True)

            stream_predict_table_nb = Datasheet.load("predictions/twitter/nb_twitter.csv")
            index_pred_nb = dict.fromkeys(stream_predict_table_nb.columns[0], True)

            stream_predict_table_svm = Datasheet.load("predictions/twitter/svm_twitter.csv")
            index_pred_svm = dict.fromkeys(stream_predict_table_svm.columns[0], True)

            stream_corpus_table_nb = Datasheet.load("corpora/twitter/tweets_stream_data_nb.csv")
            index_corp_nb = dict.fromkeys(stream_corpus_table_nb.columns[0], True)
  
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
            index_corp_ensemble =  dict.fromkeys(ensemble_table.columns[0], True)
            ensemble_table_negative = Datasheet.load("predictions/ensenmble/ensenmble_negative.csv")
            index_corp_ensemble_negative = dict.fromkeys(ensemble_table_negative.columns[0], True)
        except:
            ensemble_table = Datasheet()
            index_corp_ensemble = {}

            ensemble_table_negative = Datasheet()
            index_corp_ensemble_negative = {}

            print "Error Loading Ensemble Model CSV Files...."

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
                print "----------------------------------------------------Instance %s-----------------------------------------------------------------------------------------" % counter
                                
                langDetect = LangDetect()
                lang = langDetect.lang_detect(twt.text)
                
                print "Tweet: %s" % twt.text
                print "language: %s" %  lang
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
                        
                        if len(ensemble_table) == 0 or id not in index_corp_ensemble:
                            ensemble_table.append([id, twt.text, label, twt.date])
                            index_corp_ensemble[id] = True

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
                       
                                print '____Summary___'
                                print 'Tweet Label: %s. Storing in database' % label
                                print 'Disease Named Entity: %s, Location Named Entity: %s' % (tweet.disease_type, location)

                        tweet.save()

                    elif "negative" in nb_label and "negative" in svm_label:
                        print '____Summary___'
                        print 'Tweet Labels: NB - %s, SVM - %s; Storing in corpus' %  (nb_label, svm_label)
                      
                        if len(ensemble_table_negative) == 0 or id not in index_corp_ensemble_negative:
                            ensemble_table_negative.append([id, twt.text, svm_label, twt.date])
                            index_corp_ensemble_negative[id] = True

                    elif "positive" in nb_label and "negative" in svm_label:
                        print '____Summary___'
                        print 'Tweet Labels: NB - %s, SVM - %s; Storing in tweet corpus' %  (nb_label, svm_label)

                        if len(stream_corpus_table_svm) == 0 or id not in index_corp_svm:
                            stream_corpus_table_svm.append([id, twt.author, twt.text, svm_label, twt.date])
                            index_corp_svm[id] = True

                        if len(stream_predict_table_nb) == 0 or id not in index_pred_nb:
                            stream_predict_table_nb.append([id, twt.author, twt.text, nb_label, twt.date])
                            index_pred_nb[id] = True

                    elif "negative" in nb_label and "positive" in svm_label:
                        print '____Summary___'
                        print 'Tweet Labels: NB - %s, SVM - %s; Storing in tweet corpus' %  (nb_label, svm_label)
                      
                        if len(stream_corpus_table_nb) == 0 or id not in index_corp_nb:
                            stream_corpus_table_nb.append([id, twt.author, twt.text, nb_label, twt.date])
                            index_corp_nb[id] = True

                        if len(stream_predict_table_svm) == 0 or id not in index_pred_svm:
                            stream_predict_table_svm.append([id, twt.author, twt.text, svm_label, twt.date])
                            index_pred_svm[id] = True

                ensemble_table.save("predictions/ensenmble/ensenmble.csv")
                ensemble_table_negative.save("predictions/ensenmble/ensenmble_negative.csv")
                stream_predict_table_nb.save("predictions/twitter/nb_twitter.csv") 
                stream_predict_table_svm.save("predictions/twitter/svm_twitter.csv")
                stream_corpus_table_nb.save("corpora/twitter/tweets_stream_data_nb.csv")
                stream_corpus_table_svm.save("corpora/twitter/tweets_stream_data_svm.csv")
            # Clear the buffer every so often.
            stream_api.clear()

            # Wait awhile between polls.
            #time.sleep(1)   

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

            print "Loading and Initializing Model, Connecting to Google Search...."

            patterns_nb = NB2()
            patterns_svm = SVMLearner()

            google_corpus_table_nb = Datasheet.load("corpora/google/google_corpus_data_nb.csv")
            index_corp_nb = dict.fromkeys(google_corpus_table_nb.columns[0], True)

            google_predict_table_nb = Datasheet.load("predictions/NB/nb_google.csv")
            index_pred_nb = dict.fromkeys(google_predict_table.columns[0], True)

            google_corpus_table_svm = Datasheet.load("corpora/google/google_corpus_data_svm.csv")
            index_corp_svm = dict.fromkeys(google_corpus_table_svm.columns[0], True)

            google_predict_table_svm = Datasheet.load("predictions/SVM/svm_google.csv")
            index_pred_svm = dict.fromkeys(google_predict_table_svm.columns[0], True)

        except:
            google_corpus_table_nb = Datasheet()
            index_corp_nb = {}
            
            google_predict_table_nb = Datasheet()
            index_pred_nb = {}    

            google_corpus_table_svm = Datasheet()
            index_corp_svm = {}
            
            google_predict_table_svm = Datasheet()
            index_pred_svm = {}            
            
        for disease in ("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, \
            Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, \
            Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, \
            H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS"):

            taxonomy.append(disease, type="disease")

        p = "DISEASE" # Search pattern.

        for i in range(1,10):
            counter = 0

            for result in engine.search(q, start=i, count=100, type=SEARCH):

                counter +=1
                print "----------------------------------------------------Instance %s-----------------------------------------------------------------------------------------" % counter

                s = result.text
                s = plaintext(s)

                print "Extracted document: %s" % s
                print "Extracted URL: %s" % result.url

                langDetect = LangDetect()
                lang = langDetect.lang_detect(s)
                                
                print "Language: %s" % lang

                if ('en' in lang):
                    #model = NaiveBayes() Undeploying model
                    #classifier = model.buildModel() Undeploying classifier
                    nb_label = patterns_nb.classify(s)
                    svm_label = patterns_nb.classify(s)

                    print "NB Label: %s" % nb_label
                    print "SVM Label: %s" % svm_label                        

                    id_nb = str(hash(nb_label + plaintext(result.text)))
                    id_svm = str(hash(svm_label + plaintext(result.text)))

                    if (nb_label =='positive' and svm_label == 'positive'):

                        label = nb_label

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
                       
                        geolocation = LocationDetect()
                        country = geolocation.extractLocation(s)
                        
                        print '____Summary___'
                        print 'Document Label: %s. Storing in database' % label  
                        
                        if (country):
                            print "Geolocation: (%.5f, %.5f)" % (geolocation.detectLocation(country)[0], geolocation.detectLocation(country)[1])
                            lat = "%.5f" % geolocation.detectLocation(country)[0]
                            lng = "%.5f" % geolocation.detectLocation(country)[1]
                         
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
                        
                        print 'Disease Named Entity: %s, Location Named Entity: %s' % (googledoc.disease_type, googledoc.location_string)
   
                        googledoc.save()
                        
                                   
                        if len(google_predict_table_nb) == 0 or id not in index_pred_nb:
                            google_predict_table_nb.append([id, nb_label, plaintext(result.text), result.date])
                            index_pred_nb[id_nb] = True

                        if len(google_predict_table_svm) == 0 or id not in index_pred_svm:
                            google_predict_table_svm.append([id, svm_label, plaintext(result.text), result.date])
                            index_pred_svm[id] = True 
                    else:
                        print 'the document is negative, storing in Google corpus'

                        if len(google_corpus_table_svm) == 0 or id not in index_corp_svm:
                            google_corpus_table_svm.append([id, s, svm_label, result.date])
                            index_corp_svm[id] = True

                        if len(google_corpus_table_nb) == 0 or id not in index_corp_nb:
                            google_corpus_table_nb.append([id, s, nb_label, result.date])
                            index_corp_nb[id] = True

            google_predict_table_nb.save("predictions/NB/nb_google.csv")
            google_corpus_table_nb.save("corpora/google/google_corpus_data_nb.csv")
            google_predict_table_svm.save("predictions/SVM/nb_google_svm.csv")
            google_corpus_table_svm.save("corpora/google/google_corpus_data_svm.csv")


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

            print "Loading and Initializing Model, Connecting to Bing Search...."

            patterns_nb = NB2()
            patterns_svm = SVMLearner()

            bing_corpus_table_nb = Datasheet.load("corpora/bing/bing_corpus_data_nb.csv")
            index_corp_nb = dict.fromkeys(bing_corpus_table_nb.columns[0], True)

            bing_predict_table_nb = Datasheet.load("predictions/NB/nb_bing.csv")
            index_pred_nb = dict.fromkeys(bing_predict_table_nb.columns[0], True)

            bing_corpus_table_svm = Datasheet.load("corpora/bing/bing_corpus_data_svm.csv")
            index_corp_svm = dict.fromkeys(bing_corpus_table_svm.columns[0], True)

            bing_predict_table_svm = Datasheet.load("predictions/SVM/svm_bing.csv")
            index_pred_svm = dict.fromkeys(bing_predict_table_svm.columns[0], True)

        except:
            bing_corpus_table_nb = Datasheet()
            index_corp_nb = {}
            
            bing_predict_table_nb = Datasheet()
            index_pred_nb = {}    

            bing_corpus_table_svm = Datasheet()
            index_corp_svm = {}
            
            bing_predict_table_svm = Datasheet()
            index_pred_svm = {}              


        q = 'coronavirus'         # Bing search query

        for disease in ("flu, swine flu, West Nile Virus, Tuberculosis, Avian Influenza, \
            Influenza, Measles, Acute Intestinal Infection, Dengue, Respiratory Syndrome, \
            Albinism, Coronavirus, Polio, Legionella, Gastroenteric Syndrome, African Swine, \
            H1N1, Hepatitis A, Ebola, Hendra Virus, Influenzavirus, Meningitis, H7N9 virus, SARS"):

            taxonomy.append(disease, type="disease")

        p = "DISEASE" # Search pattern.

        engine = webpatterns.Bing(license=None)

        for i in range(1): # max=10
            counter = 0
            for result in engine.search(q, start=1, count=100, type=SEARCH, timeout=10):


                counter +=1
                print "---------------------------------------------------- Bing Document Instance %s-----------------------------------------------------------------------------------------" % counter

                s = result.text
                s = plaintext(s)

                print "Extracted document: %s" % s
                print "Extracted URL: %s" % result.url

                langDetect = LangDetect()
                lang = langDetect.lang_detect(s)
                                
                print "Language: %s" % lang

                if ('en' in lang):

                    nb_label = patterns_nb.classify(s)
                    svm_label = patterns_nb.classify(s)

                    print "NB Label: %s" % nb_label
                    print "SVM Label: %s" % svm_label                        

                    id_nb = str(hash(nb_label + plaintext(result.text)))
                    id_svm = str(hash(svm_label + plaintext(result.text)))

                    if (nb_label =='positive' and svm_label == 'positive'):
                        label = nb_label
                        bingdoc = BingDocument()
                        bingdoc.document = s
                        bingdoc.label = label
                        bingdoc.save()
                        
                        diseasetype = DiseaseType()
                        diseases = diseasetype.typedetect(s)
 
                        if diseases:
                            if (len(diseases) > 1):
                                bingdoc.disease_type = ','.join(diseases)
                            else:
                                bingdoc.disease_type = diseases[0]

                        geolocation = LocationDetect()
                        country = geolocation.extractLocation(s)
                        
                        print '____Summary___'
                        print 'Document Label: %s. Storing in database' % label  

                        if (country):
                            print "Geolocation: (%.5f, %.5f)" % (geolocation.detectLocation(country)[0], geolocation.detectLocation(country)[1])
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
                        
                        print 'Disease Named Entity: %s, Location Named Entity: %s' % (bingdoc.disease_type, bingdoc.location_string)
                        bingdoc.save()
                                   
                        print 'Document is Negative, storing in Bing corpus'

                        if len(bing_corpus_table_svm) == 0 or id not in index_corp_svm:
                            bing_corpus_table_svm.append([id, s, svm_label, result.date])
                            index_corp_svm[id] = True

                        if len(bing_corpus_table_nb) == 0 or id not in index_corp_nb:
                            bing_corpus_table_nb.append([id, s, nb_label, result.date])
                            index_corp_nb[id] = True
                 
                    else:
                        print 'Document is negative, storing in Bing corpus'

                        if len(bing_corpus_table_svm) == 0 or id not in index_corp_svm:
                            bing_corpus_table_svm.append([id, s, svm_label, result.date])
                            index_corp_svm[id] = True

                        if len(bing_corpus_table_nb) == 0 or id not in index_corp_nb:
                            bing_corpus_table_nb.append([id, s, nb_label, result.date])
                            index_corp_nb[id] = True

            bing_predict_table_nb.save("predictions/NB/nb_bing.csv")
            bing_corpus_table_nb.save("corpora/bing/bing_corpus_data_nb.csv")
            bing_predict_table_svm.save("predictions/SVM/nb_bing_svm.csv")
            bing_corpus_table_svm.save("corpora/bing/bing_corpus_data_svm.csv")
