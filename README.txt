epidetect v0.7
========= 

Epidemic Intelligence using Text Mining and Natural Language Processing Approaches (in Python) - A Postgraduate Dissertation
version 0.7


Epidetect Execution Instruction
================================
1. Clone Epidetect project at git@github.com:soloz/epidetect.git
2. Change directory to epidetect/
3. Execute the webserver
	python manage.py runserver <port>
4. Access prototype prediction using the url below.
	http://localhost:<port>/epiweb/improved/<diseasename>; or
	http://ossa.host.cs.st-andrews.ac.uk:8000/epiweb/prototype
5. Extraction Services:
	1. Execute the shell: "python manage.py shell"
	2. Load Services: "from epi.extractor import *"
	3. Start Services:
		1. Twitter Streaming: 
			1. twitter = TweetExtractor()
			2. twitter.startServer()
		2. Google Search:
			1. google = GoogleExtractor()
			2. google.googleSearch()
		3. Bing Search:
			1. bing = BingExtractor()
			2. bing.bingsearch()

[Sample Disease Names]
1. tuberculosis
2. polio
3. coronavirus
4. dengue