from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from handlers import TagHandler

#auth = HttpBasicAuthentication(realm="My Realm")
#ad = { 'authentication': auth }

tag_resource = Resource(handler=TagHandler, **ad)

urlpatterns += patterns('',
    url(r'^tags/(?P<region_slug>[^/]+)/$', tag_resource), 
)