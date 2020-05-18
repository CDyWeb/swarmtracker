from django.db import models


class SwarmReport(models.Model):
    name = models.CharField(max_length=255, null=True, default=None, blank=True)
    email = models.CharField(max_length=255, null=True, default=None, blank=True)
    phone = models.CharField(max_length=255, null=True, default=None, blank=True)
