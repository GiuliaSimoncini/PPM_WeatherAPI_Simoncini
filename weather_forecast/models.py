from django.db import models
from django.conf import settings

# Create your models here.

class Location(models.Model):
    id = models.AutoField(primary_key = True)
    region = models.CharField(max_length = 100)
    country = models.CharField(max_length = 100)

class Condition(models.Model):
    WEATHER_CHOICES = [
        ('sunny', 'Sunny'),
        ('windy', 'Windy'),
        ('rainy', 'Rainy'),
        ('cloudy', 'Cloudy'),
    ]
    id = models.AutoField(primary_key = True)
    condition = models.CharField(max_length = 100, choices = WEATHER_CHOICES)
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    humidity = models.DecimalField(max_digits=4, decimal_places=2)
    wind_speed = models.DecimalField(max_digits=4, decimal_places=2)
    air_quality = models.DecimalField(max_digits=4, decimal_places=2) # Air quality index

class Forecast(models.Model):
    id = models.AutoField(primary_key = True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now = True) # When the forecast gets created or updated the date will be updated
    weather_alert = models.BooleanField(default = False) # If the forecast has a weather alert
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='forecasts', on_delete=models.CASCADE, null=True, blank=True) # User who created the forecast



