from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models


class SwarmUser(AbstractUser):
    auth0_profile = JSONField(null=True)
    latitude = models.DecimalField("Latitude", max_digits=10, decimal_places=6, null=True, default=None, blank=True)
    longitude = models.DecimalField("Longitude", max_digits=10, decimal_places=6, null=True, default=None, blank=True)
    max_distance_km = models.IntegerField(null=False, default=20)
    email_new_swarm = models.BooleanField(default=True)
