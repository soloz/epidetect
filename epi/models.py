from django.db import models
from datetime import datetime, timedelta
import time
from epi.epidetect import LocationDetect
import json
from nltk.tokenize import RegexpTokenizer

# Create your models here.

class LocationType(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "LocationType"
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "epi_locationtype"

    @staticmethod
    def get_all_locationtypes():
        return LocationType.objects.all()

class Location(models.Model):
    """A Location is technically a geopgraphical point (lat+long), but could be
       used to represent a large area such as a city or country. It is recursive
       via the _parent_ field, which can be used to create a hierachy (Country
       -> County -> City) in combination with the _type_ field."""
    latitude  = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="The physical longitude of this location")
    name = models.CharField(max_length=100, help_text="Name of location", db_index=True)
    parent = models.ForeignKey("Location", related_name="children", null=True, blank=True,
        help_text="The parent of this Location. It" +\
                  "is expected that the parent will be of a different LocationType, although not enforced")
    level = models.PositiveIntegerField(blank=True, default=0, db_index=True,  help_text="Two levels exist. 1, 2.")
    locationtype = models.ForeignKey(LocationType, related_name="locations", blank=True, null=True)

    class Meta:
        db_table = "epi_location"

    @staticmethod
    def get_all_locations():
        return Location.objects.all()

    def __unicode__(self):
        return self.name


class Tweet(models.Model):
    """A Tweet represents a twitter message."""
    text = models.CharField(max_length=200)
    owner = models.CharField(max_length=20)
    label = models.CharField(max_length=20)
    usage = models.CharField(max_length=20)
    disease_type = models.CharField(max_length=20, null=True)
    urlentity = models.CharField(max_length=20)
    hashtagentity = models.CharField(max_length=20)
    tweet_time = models.DateTimeField(db_index=True, default=datetime.now)
    location= models.ForeignKey(Location, null=True, blank=True)
    location_string = models.CharField(max_length=20, null=True)
    from_lang = models.CharField(max_length=20)
    
    
    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_tweet"

    @staticmethod
    def get_all_tweets():
        return Tweet.objects.all()

    @staticmethod
    def get_trends_data(disease="all"):
    	days = 7
    	data = []
    	
    	for i in range(days):
    	    startdate = datetime.today() + timedelta(days=-(days-i))
    	    enddate = datetime.today() + timedelta(days=-(days-i-1))
    	    daily_tweets = Tweet.objects.filter(tweet_time__range = [startdate,enddate], disease_type__contains=disease)
    	    current_day = startdate + timedelta(days=i)
            utc_seconds = time.mktime(current_day.timetuple())
            daily_data = [utc_seconds,len(daily_tweets)]
            data.append(daily_data)

    	return data
    
    @staticmethod
    def get_all_diseases():
        diseases = []
        for tweet in Tweet.objects.all():
            if tweet.disease_type:
                disease = tweet.disease_type.split(',')
                if len(disease) > 1:
                    disease = disease[1]
                else:
                    disease = tweet.disease_type
                if disease not in diseases:
                    diseases.append(str(disease))
              
        return diseases
        
        
    @staticmethod
    def get_map_data(disease="all"):
                
        data = []
        
        for tweet in Tweet.objects.filter(disease_type__contains = disease):
   
            if tweet.location:
                
                #lat =  tweet.location.latitude
                #lng =  tweet.location.longitude
               # name =  tweet.location.name
                
                if tweet.location.latitude and tweet.location.longitude:
                    lat = "%.5f" % tweet.location.latitude
                    lng = "%.5f" % tweet.location.longitude
                else:
                    lat = "%.5f" % 0.000000
                    lng = "%.5f" % 0.000000

                if tweet.location.name:            
                    name = "%s" % tweet.location.name
                
                try:
                    data.append([[float(lng), float(lat)], name]) 
                    
                except:
                    print "Omitting non-Unicode characters in Location geocoding"            
       
        return data

    @staticmethod
    def get_country_data(country="all"):
        if country == "all":
            pass
        else:
            country_data = Tweet.objects.filter(location_string__contains=country)

        return country_data
        
    def numberofoccurance(country):
        return len(Location.objects.filter(name__contains=country))
    
    @staticmethod
    def get_outbreak_countries(disease=all):
        tokenizer = RegexpTokenizer(r'\w+|[^\w\s]+')
        
        countries = []
        
        if disease == all:
            for location in Location.objects.all():
                country = tokenizer.tokenize(location.name)
                country = country[len(country)-1]
                
                if country not in countries:
                    countries.append(str(country))
        else:
            for tweet in Tweet.objects.filter(disease_type__contains=disease):
                if tweet.location:
                    country = tokenizer.tokenize(tweet.location.name)
                    country = country[len(country)-1]
                    country_disease_count = [str(country), \
                    len(Tweet.objects.filter(disease_type__contains=disease, \
                    location_string__contains=country)), disease]
                    
                    if country_disease_count not in countries:
                        countries.append(country_disease_count)
                    
        return countries

    @staticmethod
    def get_top_countries(country_list):
        disease_counts = []
        countries = []
                
        for country in country_list:
            disease_count = len(Tweet.objects.filter(location_string__contains=country))
            disease_counts.append(disease_count)
        
        sorted_disease_counts = Tweet.sort_countries(disease_counts)
        
        for country in country_list:
            disease_count = len(Tweet.objects.filter(location_string__contains=country))
            if country not in countries and disease_count > sorted_disease_counts[len(sorted_disease_counts) - 4]:
                countries.append(country)

        print "Top 3 countries are", countries
        
        return countries
        
    @staticmethod    
    def sort_countries(disease_counts):
        for i in range(1, len(disease_counts)):

            # i values
            print "i = ", i

            val = disease_counts[i]
            j = i - 1
            while (j >= 0) and (disease_counts[j] > val):
                disease_counts[j+1] = disease_counts[j]
                j = j - 1
            disease_counts[j+1] = val
        
        return disease_counts
    
class GoogleDocument(models.Model):
    """A Google document represents a search result from google reporting outbreak."""
    document = models.CharField(max_length=200)
    owner = models.CharField(max_length=20)
    label = models.CharField(max_length=20)
    disease_type = models.CharField(max_length=20)
    search_time = models.DateTimeField(db_index=True, default=datetime.now)
    location= models.ForeignKey(Location, null=True, blank=True)
    location_string = models.CharField(max_length=20)
    from_lang = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.document

    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_googledocument"

    @staticmethod
    def get_all_documents():
        return GoogleDocument.objects.all()

    @staticmethod
    def aggregate_by_day():
        days = 7
        data = []
        
        for i in range(days):
            startdate = datetime.today() + timedelta(days=-(days-i))
            enddate = datetime.today() + timedelta(days=-(days-i-1))
            daily_documents = GoogleDocument.objects.filter(search_time__range = [startdate,enddate])
            current_day = startdate + timedelta(days=i)
            utc_seconds = time.mktime(current_day.timetuple())
            daily_data = [utc_seconds,len(daily_documents)]
            data.append(daily_data)

        return data

    @staticmethod
    def aggregate_by_week():
        pass 

    @staticmethod
    def aggregate_by_month():
       pass 


class BingDocument(models.Model):
    """A Google document represents a search result from google reporting outbreak."""
    document = models.CharField(max_length=200)
    owner = models.CharField(max_length=20)
    label = models.CharField(max_length=20)
    disease_type = models.CharField(max_length=20)
    search_time = models.DateTimeField(db_index=True, default=datetime.now)
    location= models.ForeignKey(Location, null=True, blank=True)
    location_string = models.CharField(max_length=20)
    from_lang = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.document

    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_bingdocument"

    @staticmethod
    def get_all_documents():
        return BingDocument.objects.all()

    @staticmethod
    def aggregate_by_day():
        days = 7
        data = []
        
        for i in range(days):
            startdate = datetime.today() + timedelta(days=-(days-i))
            enddate = datetime.today() + timedelta(days=-(days-i-1))
            daily_documents = BingDocument.objects.filter(search_time__range = [startdate,enddate])
            current_day = startdate + timedelta(days=i)
            utc_seconds = time.mktime(current_day.timetuple())
            daily_data = [utc_seconds,len(daily_documents)]
            data.append(daily_data)

        return data

    @staticmethod
    def aggregate_by_week():
        pass 

    @staticmethod
    def aggregate_by_month():
       pass 


class ReportType(models.Model):
    """This class models report types; Maps, Trend Charts, Visualization and Alerts graphs."""
    report = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.status

    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_report"

    @staticmethod
    def get_all_reporttypes():
       pass 


class Disease(models.Model):
    """This class models disease types; It is intended that more diseases would be added via the GUI for future searches."""
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.status

    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_disease"

    @staticmethod
    def get_all_diseases():
       pass 
