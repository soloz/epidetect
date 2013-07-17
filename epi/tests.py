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

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestEpidetect(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestPresentation(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestExtractor(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestNaiveBayes(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """

        classifier = NaiveBayes()
        model = classifier.buildModel()

        #Sample documents obtained from corpus.
        test_tweets = []

        pos_event_tweets_test = [('there are 7 reported cases of h1n1 in zambia', 'positive'),('5 reported dead repeated cases of h1n1', 'positive'),
        ('h1n1 outbreak has been discovered near india', 'positive'),('50 people have died so far in middle east over outbreak of h1n1', 'positive'),
        ('detection of h1n1 in turkey', 'positive'), ('many hospitals have been closed down due to outbreak of h1n1', 'positive') ]

        neg_event_tweets_test = [('RT @trutherbot: Protip: Flu shots do not work.', 'negative'),
        ('Retweet this.... doctors are saying there might be a new flu, and that they don\'t have the vaccination..  http://t.co/Apk3QNjFs1', 'negative'),
        ('Nothing seems to be working for this flu...', 'negative'),
        ('EG Flu Tracking News 84 in state die of H1N1 in 6 months - Times of India http://t.co/GaDDrTiDNz', 'negative'),
        ('Flu season comes and goes, but #WordFlu season is here to stay! #NoYouWontGetSick #ItsGoingToBeFine #ItsAGame', 'negative'), 
        ('@Perrie_Ndublet I had the flu so I went to the loo', 'negative')]

        for (words, sentiment) in pos_event_tweets_test + neg_event_tweets_test:
            words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
            test_tweets.append((words_filtered, sentiment))

        word_features_test = classifier.get_word_features(classifier.get_words_in_tweets(test_tweets))
        classifier.set_word_features = word_features_test
        test_set = nltk.classify.apply_features(classifier.extract_test_features, test_tweets)

        print 'Accuracy of NaiveBayes:', nltk.classify.util.accuracy(model, test_set)
        model.show_most_informative_features(32)

        #self.assertEqual(1 + 1, 2)



class TestMovieCorpusClassifier(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
    def word_feats(words):
        return dict([(word, True) for word in words])
    
    negids = movie_reviews.fileids('neg')
    posids = movie_reviews.fileids('pos')
    
    negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
    posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

    negcutoff = len(negfeats)*3/4
    poscutoff = len(posfeats)*3/4

    trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
    testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

    print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))

    classifier = NaiveBayesClassifier.train(trainfeats)
    print 'Accuracy of Sample Corpus:', nltk.classify.util.accuracy(classifier, testfeats)
    classifier.show_most_informative_features()



        #self.assertEqual(1 + 1, 2)

