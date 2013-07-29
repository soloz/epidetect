from django.db import models
from datetime import datetime, timedelta
import time
from epi.epidetect import LocationDetect

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
    
    
    def __unicode__(self):
        return self.text

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
    def get_map_data(disease="all"):
                
        data = []
        location = LocationDetect() 
        
        for tweet in Tweet.objects.filter(disease_type__contains = disease):
       
            if tweet.location_string:
                
                geolocationInfo = location.detectLocation(tweet.location_string)
                
                if geolocationInfo: 
                    lat =  geolocationInfo[0]
                    lng =  geolocationInfo[1]
                    
                    if tweet.disease_type:
                        try:
                            data.append([[lng, lat], str(tweet.location_string)])  
                        except:
                            print "Omitting non-Unicode characters in Location geocoding"            

        return data


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
