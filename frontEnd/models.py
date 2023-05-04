import os
from django.db import models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AircraftHunting.settings")


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    pwdsuffix = models.CharField(max_length=10)

    def __str__(self):
        return self.username
