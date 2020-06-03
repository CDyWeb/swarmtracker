import uuid

from cloudinary.models import CloudinaryField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse

from swarm.models import SwarmUser

status_choices = {
    'new': 'New',
    'assigned': 'Assigned',
    'done': 'Done'
}


class SwarmReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reporter = models.ForeignKey(to=SwarmUser, null=True, default=None, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=255, default='new', blank=True, choices=[(k, v) for k, v in status_choices.items()])
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, default=None, blank=True)
    location = models.TextField(null=True, default=None, blank=True)
    latitude = models.DecimalField("Latitude", max_digits=10, decimal_places=6, validators=[])
    longitude = models.DecimalField("Longitude", max_digits=10, decimal_places=6, validators=[])
    location_reverse = JSONField(null=True, default=None, blank=True)

    def __str__(self):
        return self.uri

    @property
    def uri(self):
        return reverse('swarm-details', kwargs={'uuid': self.id})

    def status_str(self):
        return status_choices.get(self.status)

    '''
    {"type": "s", 
    "latLng": {"lat": 44.22315, "lng": -76.49395}, 
    "linkId": "0", 
    "mapUrl": "http://open.mapquestapi.com/staticmap/v5/map?key=...&type=map&size=225,160&locations=44.22315048127559,-76.49394972451707|marker-sm-50318A-1&scalebar=true&zoom=15&rand=1435158634", 
    "street": "71 King Street West", 
    "dragPoint": false, 
    "adminArea1": "CA", 
    "adminArea3": "ON", 
    "adminArea4": "", 
    "adminArea5": "Kingston", 
    "adminArea6": "", 
    "postalCode": "K7L3T4", 
    "sideOfStreet": "N", 
    "unknownInput": "", 
    "displayLatLng": {"lat": 44.22315, "lng": -76.49395}, 
    "adminArea1Type": "Country", 
    "adminArea3Type": "State", 
    "adminArea4Type": "County", 
    "adminArea5Type": "City", 
    "adminArea6Type": "Neighborhood", 
    "geocodeQuality": "POINT", 
    "geocodeQualityCode": "P1AAA"}
    '''
    @property
    def location_str(self):
        return ', '.join([
            self.location_reverse.get('street'),
            self.location_reverse.get('adminArea5')
        ])

    @property
    def location_map(self):
        return self.location_reverse.get('mapUrl').replace('&size=225,160&', '&size=480,320&')


class SwarmNote(models.Model):
    author = models.ForeignKey(to=SwarmUser, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    swarm = models.ForeignKey(to=SwarmReport, on_delete=models.PROTECT, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    note = models.TextField()

    @property
    def author_or_contact(self):
        return self.author.first_name or self.swarm.name


class SwarmPhoto(models.Model):
    swarm = models.ForeignKey(to=SwarmReport, on_delete=models.PROTECT, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    image = CloudinaryField('image')

    """ Informative name for model """
    def __unicode__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s>" % public_id

    @property
    def src_100(self):
        return self.image.build_url(width=100, height=65, crop="fill")

    @property
    def src_800(self):
        return self.image.build_url(width=800, height=600, crop="limit")
