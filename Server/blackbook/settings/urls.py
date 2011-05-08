from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
#from staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from iconography.views import *

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
)

urlpatterns += patterns('',
        url(r'^$', index, {}),
    )

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
