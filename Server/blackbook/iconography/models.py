import datetime

import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from geopy import geocoders

from django.contrib.auth.models import User
from django.contrib.localflavor.us import models as lfus_models

__all__ = (
    'Root', 'EphemeralRoot', 'EphemeralRootManager', 'CoordinateModel',
    'AddressableCoordinateModel',
)

class EphemeralRootManager(models.GeoManager):
    def moderated(self):
        return self.filter(approved_at__isnull=False)

    def awaiting_moderation(self):
        return self.filter(approved_at__isnull=True)

    def accepted(self):
        # Return all objects until we have a full moderation system.
        return self.all()
        #return self.moderated().filter(enabled=True)

    def rejected(self):
        return self.moderated().filter(enabled=False)

    def enabled(self):
        return self.filter(enabled=True)

    def disabled(self):
        return self.filter(enabled=False)

class Root(models.Model):
    name = models.CharField(db_index=True, max_length=255) 

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    modified = models.DateTimeField(db_index=True, auto_now=True)
    expires = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        abstract = True

class EphemeralRoot(Root):
    enabled = models.BooleanField(db_index=True, default=True)

    approved_at = models.DateTimeField(db_index=True, null=True, blank=True)

    #Change to moderated_by
    approved_by = models.ForeignKey(
        User, null=True, blank=True,
        related_name='%(app_label)s_%(class)s_approved'
    )

    objects = EphemeralRootManager()

    @property
    def is_approved(self):
        return self.approved_at is not None

    @is_approved.setter
    def is_approved(self, value):
        self.approved_at = datetime.now() if value == True else None

    class Meta:
        abstract = True

class CoordinateModel(models.Model):
    coordinates = models.PointField(null=True, blank=True)
    location = models.CharField(max_length=300, blank=True)

    def get_current_location(self):
        return None

    def save(self, *args, **kwargs):
        cur_location = self.get_current_location()

        if cur_location is not None and cur_location != self.location:
            g = geocoders.Google(settings.GOOGLE_API_KEY)
            try:
                for place, point in g.geocode(cur_location, exactly_one=False):
                    self.latitude, self.longitude = point
                    self.location = cur_location
            except:
                pass

        super(CoordinateModel, self).save(*args, **kwargs)

    def _get_coordinates(self):
        if not self.coordinates:
            self.coordinates = Point(0,0)
        return self.coordinates

    def _set_coordinates_part(self, attr, val):
        coordinates = self._get_coordinates()
        setattr(coordinates, attr, val)

    @property
    def latitude(self):
        return self._get_coordinates().y

    @latitude.setter
    def latitude(self, val):
        self._set_coordinates_part('y', val)

    @property
    def longitude(self):
        return self._get_coordinates().x

    @longitude.setter
    def longitude(self, val):
        self._set_coordinates_part('x', val)

    class Meta:
        abstract = True

class AddressableCoordinateModel(CoordinateModel):
    address_0 = models.CharField(verbose_name='Address', max_length=255)
    address_1 = models.CharField(
        verbose_name='Apt, Suite, Bldg', blank=True, null=True, max_length=100
    )

    city = models.CharField(max_length=100)
    state = lfus_models.USStateField()
    zipcode = models.CharField(max_length=10)

    def get_current_location(self):
        return u'%s%s %s, %s %s' % (
            self.address_0, ' '+self.address_1 if self.address_1 else '',
            self.city, self.state, self.zipcode
        )

    class Meta:
        abstract = True


##
# Asset models
###

from django.contrib.gis.db import models
from iconography.models import CoordinateModel, EphemeralRoot

__all__ = (
    'Tag', 'LightMap',
)

YEAR_IN_SCHOOL_CHOICES = (
    ('0', 'I Could Eat?'),
    ('1', 'Step Sister\'s Panties'),
    ('2', 'Rough Handjob'),
    ('3', 'Free Candy'),
    ('4', 'Bitchin\' Camero'),
)

MARKER_TYPE = (
    ('ass', 'NFT Asset'),
    ('pat', 'AR Pattern'),
)

class Tag(CoordinateModel, EphemeralRoot):
    icon = models.ImageField(upload_to='dynamic/icon')
    asset = models.FileField(upload_to='dynamic/asset')
    radius = models.IntegerField(blank=True, null=True)

    marker_type = models.CharField(max_length=4, choices=MARKER_TYPE)


    def __str__(self):
        #fuck_it = u'\xfc'
        return unicode(self.name)

class LightMap(CoordinateModel, EphemeralRoot):
    map = models.ImageField(upload_to='dynamic/icon')

    def __str__(self):
        #fuck_it = u'\xfc'
        return unicode(self.name)