#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.web import SEARCH
from pattern.web import Google, Twitter, Facebook, Bing


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


class Geologic:
    ''' This class holds method stubs and some utilities for 
        performing geolocation, geocoding and geonaming of 
        locations.
    '''
       
    def geocode(self, *args, **kwargs):
        ''' Perform geocoding of locations.
        '''
        pass

    def geolocate(self, *args, **kwargs):
        ''' Perform geolocation of disease locations.
        '''
        pass

    def geoname(self, *args, **kwargs):
        ''' Perform mapping of locations in documents to 
        actual disease locations.
        '''
        pass


class Utility:
    ''' This class is a utility class to perform extra tasks 
        not performed by other classes.
    '''
       
    def performAction(self, *args, **kwargs):
        ''' Perform undefined actions.
        '''
        pass