from django.db import models

# Create your models here.

class Tweet(models.Model):
    status = models.CharField(max_length=200)
    owner = models.CharField(max_length=20)
    latitude  = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical longitude of this location")

    def __unicode__(self):
        return self.status

    def getStatus(self):
    	pass
