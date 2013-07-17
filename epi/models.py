from django.db import models
import datetime

# Create your models here.

class LocationType(models.Model):
    name = models.CharField(max_length=100)
    
    
    class Meta:
        verbose_name = "LocationType"
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "epi_locationtype"

class Location(models.Model):
    """A Location is technically a geopgraphical point (lat+long), but could be
       used to represent a large area such as a city or country. It is recursive
       via the _parent_ field, which can be used to create a hierachy (Country
       -> County -> City) in combination with the _type_ field."""
    latitude  = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical longitude of this location")
    name = models.CharField(max_length=100, help_text="Name of location", db_index=True)
    parent = models.ForeignKey("Location", related_name="children", null=True, blank=True,
        help_text="The parent of this Location. It" +\
                  "is expected that the parent will be of a different LocationType, although not enforced")
    level = models.PositiveIntegerField(blank=True, default=0, db_index=True,  help_text="Two levels exist. 1, 2.")
    locationtype = models.ForeignKey(LocationType, related_name="locations", blank=True, null=True)

    class Meta:
        db_table = "epi_location"

class Tweet(models.Model):
    """A Tweet represents a twitter message."""
    text = models.CharField(max_length=200)
    owner = models.CharField(max_length=20)
    label = models.CharField(max_length=20)
    usage = models.CharField(max_length=20)
    source = models.CharField(max_length=20)
    urlentity = models.CharField(max_length=20)
    hashtagentity = models.CharField(max_length=20)
    tweet_time = models.DateTimeField(db_index=True, default=datetime.datetime.now)
    location= models.ForeignKey(Location, null=True, blank=True)
    
    def __unicode__(self):
        return self.text

    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_tweet"

    @staticmethod
    def get_all_tweets():
        return Tweet.objects.all()


class Reports(models.Model):
    """This class models report types; Maps, Trend Charts, Visualization and Alerts graphs."""
    report = models.CharField(max_length=20)
    
    
    def __unicode__(self):
        return self.status

    def getStatus(self):
        pass

    class Meta:
        db_table = "epi_reports"