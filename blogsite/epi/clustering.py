#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.web import SEARCH
from pattern.web import Google, Twitter, Facebook, Bing
from classification import Classifier


class ClusterManager:
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


class Positive:
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

class Negative:
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
        

class Unknown:
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


class NonEnglish:
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