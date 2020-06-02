from django.contrib.auth.models import AbstractUser
from django.db import models


class SwarmUser(AbstractUser):
    full_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    phone = models.CharField(max_length=255, null=True, blank=True, default=None)
    zip = models.CharField(max_length=255, null=True, blank=True, default=None)
    latitude = models.DecimalField("Latitude", max_digits=10, decimal_places=6, null=True, default=None, blank=True)
    longitude = models.DecimalField("Longitude", max_digits=10, decimal_places=6, null=True, default=None, blank=True)
    max_distance_km = models.IntegerField(null=False, default=20)
    email_new_swarm = models.BooleanField(default=True)
