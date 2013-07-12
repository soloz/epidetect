#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.vector import *
from pattern.web import Google, Twitter, Facebook, Bing
from epidetect import Evaluator
import nltk


class NaiveBayes:
    ''' This class implements the Naive Bayes text classifciation algorithm.
    '''
    def __init__(self):
        pass

    def buildModel(self):
        ''' Perform model building and intermittent model optimizations based on training corpus.
        '''
        global word_features
        global classifier

        #Sample documents obtained from corpus.
        pos_tweets = [('I love this car', 'positive'),('This view is amazing', 'positive'),
        ('I feel great this morning', 'positive'),('I am so excited about the concert', 'positive'),
        ('He is my best friend', 'positive')]

        neg_tweets = [('I do not like this car', 'negative'),('This view is horrible', 'negative'),
        ('I feel tired this morning', 'negative'),('I am not looking forward to the concert', 'negative'),('He is my enemy', 'negative')]

        tweets = []

        pos_event_tweets = [('10 cases of h1n1 has been reported in london', 'positive'),('5 killed in saudi of h1n1', 'positive'),
        ('10 people have been said to contract h1n1', 'positive'),('25 people infected with h1n1 now in the hospital in argentina', 'positive'),
        ('traces of h1n1 recorded near turkey', 'positive'), ('private hospitals advised to close down because of the noticed h1n1', 'positive'),
         ('2 people dead from h1n1 virus', 'positive')        ]

        neg_event_tweets = [('how to take care of h1n1', 'negative'),('h1n1 and how to prevent it', 'negative'),
        ('i\'m having flu', 'negative'),('is h1n1 a deluge in the 21st century ?', 'negative'),
        ('how are we affected by upsurge in the h1n1 recently', 'negative'), ('is this h1n1 or what ?', 'negative'),
        ('what are the symptoms of h1n1 virus', 'negative')]


        for (words, sentiment) in pos_event_tweets + neg_event_tweets:
            words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
            tweets.append((words_filtered, sentiment))

        word_features = self.get_word_features(self.get_words_in_tweets(tweets))
        
        training_set = nltk.classify.apply_features(self.extract_features, tweets)
        print training_set

        classifier = nltk.NaiveBayesClassifier.train(training_set)
        print classifier.show_most_informative_features(32)

        return classifier


    def get_words_in_tweets(self, documents):
        ''' Method to obtain words from documents or tweets obtained 
            from documents corpora, in order to build features from them.
            Word feature names are used to build the classifier/model.
        '''
        all_words = []
        for (words, sentiment) in documents:
            all_words.extend(words)

        return all_words

    def get_word_features(self, wordlist):
        ''' Method for extracting word features used to build the classifier/model.
            Classifier gets better with more word features to feed into classifier.
        '''
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    def extract_features(self, document):
        ''' Method for extracting word features from new documents.
        '''
        document_words = set(document)
        features = {}

        for word in word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features    


    def classify(self, *args):
        ''' Performs classification of new documents.
        '''
        print args[1].classify(self.extract_features(args[0].split()))


class KMeansLeaner:
    ''' This class holds method stubs and some utilities for 
        implementing the k-means algorithm.
    '''
       
    def learn(self, *args, **kwargs):
        ''' Perform learning of a Model from training data.
        '''
        pass

    def buildModel(self, *args, **kwargs):
        ''' Performs model building.
        '''
        pass


class SVMLearner:
    ''' This class holds method stubs and some utilities for 
        implementing the Support Vector Machine (SVM) algorithm.
    '''
    
    def learn(self, *args, **kwargs):
        ''' Perform learning of a Model from training data using SVM algorithm.
        '''
        pass

    def buildModel(self, *args, **kwargs):
        ''' Performs model building from training using SVM algorithm.
        '''
        pass

class Classifier:
    ''' This class holds method stubs and some utilities for 
        performing document classification using keywords.
    '''
       
    def classify(self, *args, **kwargs):
        ''' Perform classification of documents using keywords.
        '''
        pass

    def buildModel(self, *args, **kwargs):
        ''' Performs model building from training data.
        '''
        pass