from django.contrib.gis.db import models
from django.contrib.gis.geo import Point

# Create your models here.

YEAR_IN_SCHOOL_CHOICES = (
    ('0', 'I Could Eat?'),
    ('1', 'Step Sister\'s Panties'),
    ('2', 'Rough Handjob'),
    ('3', 'Free Candy'),
    ('4', 'Bitchin\' Camero'),
)

class Tag(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='dynamic/icon')
    asset = models.FileField(upload_to='dynamic/asset')
    point = models.PointField(null=True, blank=True)
    radius = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        #fuck_it = u'\xfc'
        return unicode(self.name)