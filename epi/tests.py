"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from epi.classification import NaiveBayes 
from epi.epidetect import *
from geopy import geocoders  

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestLanguageTranslation(TestCase):
    def test_translate(self):
        """
        Testing translation of language using Google Translate API.
        """
        pass
        
        #text = 'Inverno atipico deixa Salvador em alerta para epidemia de dengue http://t.co/ukSEdpiLxk'
        #translation = 'Winter leaves atypical Salvador alert for dengue epidemic http://t.co/ukSEdpiLxk'
        
        #l = LangTranslate()
        #translated_text = l.translate(text, 'pt')
        
        #self.assertEqual(translation, translated_text)

class TestDiseaseType(TestCase):
    def test_diseasetype(self):
        """
        Tests to determine or ascertain disease type contains in documents/reports.
        """
        document = "First confirmed death from H1N1 flu virus in Rivers. http://t.co/MNDQfbIu4a #H1N1 #SwineFlu"
        disease_types = ['flu', 'h1n1']
        
        dd = DiseaseType()
        detected_types = dd.typedetect(document)
        
        self.assertEqual(disease_types, detected_types)


class TestExtractor(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class TestLangDetect(TestCase):
    def test_lang_detect(self):
        lang_detect = LangDetect()
        lang = 'english'

        text = 'RT @ottawasuncom: West Nile virus has been found in mosquitoes in Perth, about 80k west of Ottawa, local health unit reports...'
        detected_lang = lang_detect.lang_detect(text)

        self.assertEqual(lang, detected_lang)
        
    def test_lang_likelihood(self):
        lang_likelihood = {'swedish': 1, 'danish': 1, 'hungarian': 1, 'finnish': 0, 'portuguese': 3, 'german': 0, 'dutch': 1, 'french': 2, 'spanish': 2, 'norwegian': 1, 'english': 1, 'russian': 0, 'turkish': 1, 'italian': 0}
        text = 'Inverno atipico deixa Salvador em alerta para epidemia de dengue http://t.co/ukSEdpiLxk'
        
        lang_detect = LangDetect()
        
        detected_likelihood = lang_detect.lang_likelihood(text)
        
        self.assertEqual(lang_likelihood, detected_likelihood)
        
class TestLocationDetect(TestCase):
    def test_detectLocation(self):
            
        location = (55.598057999999988, -4.4517390000000008, u'Hurlford, East Ayrshire, UK')
        location_text = 'Hurlford, East Ayrshire, UK'
        
        loc_detect = LocationDetect()
        (lat, lng, place) = loc_detect.detectLocation(location_text)

        self.assertEqual(location, (lat, lng, place))
        
    def test_getTweetLocation(self):
        user = 'theopendaily'
        location = 'Los Angeles' 
        
        loc_detect = LocationDetect()
        
        userlocation = loc_detect.getTweeterLocation(user)
        
        self.assertEqual(location, userlocation)
    def test_getTweetLocation(self):
        location = 'Pakistan'
        text = '@shahalam13 Sounds a lot like Pakistan\'s woes, although Pak has religious extremists killing polio volunteers to add to their challenges.'
        
        loc_detect = LocationDetect()
        
        extracted_location = loc_detect.extractLocation(text)
        
        self.assertEqual(location, extracted_location)
   
        
class TestTweetExtractor(TestCase):
    def test_tweet_stream(self):
	    pass
