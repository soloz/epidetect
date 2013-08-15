#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from pattern.vector import *
from pattern.web import Google, Twitter, Facebook, Bing
from epidetect import Evaluator
import nltk
from epi.models import Tweet, Location, LocationType
from pattern.en     import tag, predicative 
from pattern.db  import Datasheet, pprint, csv
import pickle


class NaiveBayes:
    ''' This class implements the Naive Bayes text classifciation algorithm.
    '''
    def __init__(self):
        self.word_features_test =[]
        self.word_features_train = []
        
        try:
            self.modelfile = open('models/nb_model2.ept', 'r')
            self.loadedclassifier = pickle.load(self.modelfile)
        except:
            print "Something is wrong with loading"

    def buildModel(self):
        ''' This method performs model building and intermittent model 
        optimizations based on trained corpus. Naive Bayes classifier has been
        used in training a model.
        '''
        #global word_features_train
        global classifier
        #global word_features_test

        #Sample documents obtained from corpus.
        train_tweets = []
        test_tweets = []
        pos_event_tweets_train = []
        neg_event_tweets_train = []
        pos_event_tweets_test = []
        neg_event_tweets_test = []

        #Load training data from CSV
        data = Datasheet.load(os.path.join("corpora","twitter","positivedatabasedump.csv"))

        #Building Training set
        for doc, label in data[100:]:
            #Positive instances of tweets for training
            if "positive" in label:
                pos_event_tweets_train.append((doc, str(label))) 
            else:
            #Negative instances of tweets for training model.
                neg_event_tweets_train.append((doc, str(label))) 

        #Building Training set
        for doc, label in data[:100]:
            #Positive instances of tweets for training
            if "positive" in label:
                pos_event_tweets_test.append((doc, str(label))) 
            else:
            #Negative instances of tweets for training model.
                neg_event_tweets_test.append((doc, str(label))) 


        #Training model using the document corpus above.
        for (words, sentiment) in pos_event_tweets_train + neg_event_tweets_train:
            words_filtered = [e.lower() for e in words.split() if len(e) > 3]
            train_tweets.append((words_filtered, sentiment))

        #Testing model using test corpus. 
        for (words, sentiment) in pos_event_tweets_test + neg_event_tweets_test:
            words_filtered = [e.lower() for e in words.split() if len(e) > 3]
            test_tweets.append((words_filtered, sentiment))

        #Building word features
        self.word_features_train = self.get_word_features(self.get_words_in_tweets(train_tweets))
        self.word_features_test = self.get_word_features(self.get_words_in_tweets(test_tweets))

        training_set = nltk.classify.apply_features(self.extract_train_features, train_tweets)
        test_set = nltk.classify.apply_features(self.extract_test_features, test_tweets)

        #Building a classifier.
        classifier = nltk.NaiveBayesClassifier.train(training_set)
        print 'accuracy:', nltk.classify.util.accuracy(classifier, test_set)

        print classifier.show_most_informative_features(32)

        print "Saving model to file models/nb_model2.ept."

        modelfile = open('models/nb_model2.ept', 'w')
        pickle.dump(classifier, modelfile)
        modelfile.close()

        modelf = open('models/nb_model2.ept', 'r')
        classf=pickle.load(modelf)
        print 'accuracy:', nltk.classify.util.accuracy(classf, test_set)

        return classifier

    def testModel(self):
        #Load training data from CSV
        data = Datasheet.load(os.path.join("corpora","twitter","positivedatabasedump.csv"))
        test_tweets = []
        pos_event_tweets_test = []
        neg_event_tweets_test = []

        for doc, label in data[:100]:
            #Positive instances of tweets for training
            if "positive" in label:
                pos_event_tweets_test.append((doc, str(label))) 
            else:
            #Negative instances of tweets for training model.
                neg_event_tweets_test.append((doc, str(label))) 

        for (words, sentiment) in pos_event_tweets_test + neg_event_tweets_test:
            words_filtered = [e.lower() for e in words.split() if len(e) > 3]
            test_tweets.append((words_filtered, sentiment))
        
        test_set = nltk.classify.apply_features(self.extract_test_features, test_tweets)

        print 'accuracy:', nltk.classify.util.accuracy(self.loadedclassifier, test_set)

        print self.loadedclassifier.show_most_informative_features(32)


    def get_words_in_tweets(self, documents):
        ''' Method to obtain words from documents or tweets obtained 
            from documents corpora, in order to build features from them.
            Word feature names are used to build the classifier/model.
        '''
        all_words = []
        for (words, sentiment) in documents:
            all_words.extend(words)

        return all_words

    def set_word_feature(self, word_features):
        self.word_features_test = word_features

    def get_word_features(self, wordlist):
        ''' Method for extracting word features used to build the classifier/model.
            Classifier gets better with more word features to feed into classifier.
        '''
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    def extract_train_features(self, document):
        ''' Method for extracting word features from new documents.
        '''
        document_words = set(document)
        features = {}

        for word in self.word_features_train:
            features['contains(%s)' % word] = (word in document_words)
        return features    

    def extract_test_features(self, document):
        ''' Method for extracting word features from new documents.
        '''
        document_words = set(document)
        features = {}

        for word in self.word_features_test:
            features['contains(%s)' % word] = (word in document_words)
        return features  

    def classify_old(self, *args):
        ''' Performs classification of new documents.
        '''
        label = args[1].classify(self.extract_train_features(args[0].split()))

        return label

    def classify(self, *args):
        ''' Performs classification of new documents.
        '''
        label = self.loadedclassifier.classify(self.extract_train_features(args[0].split()))

        return label

class NB2:
    ''' This class holds method stubs and some utilities for 
        implementing the second implementation of Naive Bayes algorithm.
    '''

    def testModel(self, *args):
        ''' Perform learning of a Model from training data.
        '''
        documents = []
        data = Datasheet.load(os.path.join("corpora","twitter","positivedatabasedump.csv"))

        if args:
            classifier = Classifier.load('models/nb_model.ept')
            print "Document class is %s" % classifier.classify(Document(args[0]))
            print "Document probability is : ", classifier.classify(Document(args[0]), discrete=False) 
            label = classifier.classify(Document(args[0]), discrete=False)

            print label["positive"]

        else:
            i = n = 0
            classifier = Classifier.load('models/nb_model.ept')
            data = shuffled(data)

            for document, label in data[:100]:
                doc_vector = Document(document, type=str(label), stopwords=True)
                documents.append(doc_vector)
     
            print "10-fold CV"
            print k_fold_cv(NB, documents=documents, folds=10)


        print "Classes in Naive Bayes Classifier"
        print classifier.classes

        print "Area Under the Curve: %0.6f" % classifier.auc(documents, k=10)

        print "Model Performance"
        accuracy, precision, recall, f1 = classifier.test(data[:100])

        print "Accuracy = %.6f; F-Score = %.6f; Precision = %.6f; Recall = %.6f" % (accuracy, f1, precision, recall)

        print "Confusion Matrix"
        print classifier.confusion_matrix(data[:100])(True)



    def buildModel(self, *args, **kwargs):
        ''' Performs model building.
        '''

        #initializing Naive Bayes package
        classifier = NB()
        documents = []

        print "loading document corpus..."
        data = Datasheet.load(os.path.join("corpora","twitter","positivedatabasedump.csv"))
        data = shuffled(data)

        print "training svm model..."

        for document, label in data[100:]:
            doc_vector = Document(document, type=str(label), stopwords=True)
            classifier.train(doc_vector)
            
        #Saving model to file system.
        try:
            print "saving build model..."
            classifier.save('models/nb_model.ept')
        except:
            print "cannot save model file for some reason"

    def classify(self, document):
        ''' This method is used to classify new documents. Uses the saved model.
        '''
        
        #Loading csv predictions and corpora documents.
        try: 
            nb_predictions = Datasheet.load("predictions/NB/patterns_nb.csv")
            nb_corpus = Datasheet.load("corpora/NB/nb.csv")

            index_pred = dict.fromkeys(nb_predictions.columns[0], True)
            index_corp = dict.fromkeys(nb_corpus.columns[0], True)
        except:
            nb_predictions = Datasheet()
            nb_corpus = Datasheet()
            index_pred = {}
            index_corp = {}

        #Load model from file system
        classifier = Classifier.load('models/nb_model.ept')
        label = classifier.classify(Document(document))
        probability = classifier.classify(Document(document), discrete=False)[label]

        id = str(hash(label + document))

        if ("positive" in label):
            if len(nb_predictions) == 0 or id not in index_pred:
                nb_predictions.append([id, label, document, probability])
                index_pred[id] = True
                
        if len(nb_corpus) == 0 or id not in index_corp:
            nb_corpus.append([id, label, document, probability])
            index_corp[id] = True

        nb_predictions.save("predictions/NB/patterns_nb.csv")
        nb_corpus.save("corpora/NB/nb.csv")

        return label

class SVMLearner:
    ''' This class holds method stubs and some utilities for 
        implementing the Support Vector Machine (SVM) algorithm.
    '''
        
    global classifier

    def testModel(self, *args):
        ''' This method performs model testing.
        '''

        documents = []    
        data = Datasheet.load(os.path.join("corpora","twitter","positivedatabasedump.csv"))

        if args:
            classifier = Classifier.load('models/svm_model3_probability.ept')
            print "Document class is %s" % classifier.classify(Document(args[0]))
            print "Document probability is " 
            print classifier.classify(Document(args[0]), discrete=False)

        else:
            i = n = 0
            classifier = Classifier.load('models/svm_model2.ept')
            data = shuffled(data)

            for document, label in data[:100]:
                if classifier.classify(Document(document)) == label:
                    i += 1
                n += 1
                documents.append(Document(document, type=label))
        

        print "Classes in Support Vector Machine Classifier"
        print classifier.classes

        print "Confusion Matrix is:"
        print classifier.confusion_matrix(data[:100])(True)

        print "SVM Model Performance"
        accuracy, precision, recall, f1 = classifier.test(data[:100])

        print "Accuracy = %.6f; F-Score = %.6f; Precision = %.6f; Recall = %.6f" % (accuracy, f1, precision, recall)

        print "Area Under the Curve: %0.6f" % classifier.auc(documents, k=10)

        print "Accuracy is:"
        print float(i) / n

        print "10-fold CV"
        print k_fold_cv(SVM, documents=documents, folds=10)


    def buildModel(self, *args, **kwargs):
        ''' Performs model building from training using SVM algorithm 
        implementation in patters.vector API.
        '''
        classifier = SVM(type = CLASSIFICATION, kernel=LINEAR, probability = True)

        print "loading document corpus..."
        data = Datasheet.load(os.path.join("corpora","twitter","positivedatabasedump.csv"))
        data = shuffled(data)

        print "training svm model..."

        for document, label in data[:460]:
            print "Document and label are", [document, label]
            classifier.train(Document(document, type=str(label)))

        #Saving model to file system.
        try:
            print "saving build model..."
            classifier.save('models/svm_model3_probability.ept')
        except:
            print "cannot save model file for some reason"

    def classify(self, document):
        ''' This method is used to classify new documents. Uses the saved model.
        '''
        
        #Loading csv predictions and corpora documents.
        try: 
            svm_predictions = Datasheet.load("predictions/svm.csv")
            svm_corpus = Datasheet.load("corpora/svm/svm.csv")

            index_pred = dict.fromkeys(svm_predictions.columns[0], True)
            index_corp = dict.fromkeys(svm_corpus.columns[0], True)
        except:
            svm_predictions = Datasheet()
            svm_corpus = Datasheet()
            index_pred = {}
            index_corp = {}

        #Load model from file system
        classifier = Classifier.load('models/svm_model2.ept')
        label = classifier.classify(Document(document))

        id = str(hash(label + document))

        if ("positive" in label):
            if len(svm_predictions) == 0 or id not in index_pred:
                svm_predictions.append([id, label, document])
                index_pred[id] = True
                
        if len(svm_corpus) == 0 or id not in index_corp:
            svm_corpus.append([id, label, document])
            index_corp[id] = True

        svm_predictions.save("predictions/svm.csv")
        svm_corpus.save("corpora/svm/svm.csv")

        return label
