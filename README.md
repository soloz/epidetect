epidetect v0.1
========= 

Epidemic Intelligence using Text Mining and Natural Language Processing Approaches (in Python) - A Postgraduate Dissertation
version 0.1


Prototype Deployment Instruction
================================
1. Clone Epidetect project at git@github.com:soloz/epidetect.git
2. Change directory to epidetect/
3. Execute the webserver
	python manage.py runserver <port>
4. Access prototype prediction using the url below.
	http://localhost:<port>/epiweb/prototype; or
	http://ossa.host.cs.st-andrews.ac.uk:8000/epiweb/prototype

Other Notes
===========
	1.) The prototype (url given above) predicts the class of new document(s)/tweets using the Naive Bayes Model implemented in this version 0.1. Two possible classes have been implemented, namely; positive or negative.
	2.) Improved Naive Bayes model planned in next version. Improvements are
			1. Use of more training data set : Up to 500 tweets (negative or positive)
	3.) Implementation of SVM model in version 0.2 or 0.3
	4.) Unit test of implemented functionalities
	5.) Project target/final dashboard showing trends, maps, charts and alerts is still available at
		http://localhost:<port>/epiweb/prototype
	6.) Other features of the tool as proposed on plan