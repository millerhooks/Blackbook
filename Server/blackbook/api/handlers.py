import re

from piston.handler import BaseHandler
from piston.utils import rc, throttle

from iconography.models import Tag

class TagHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'DELETE')
    fields = ('')
    #exclude = ()
    model = Tag

    def read(self, request, post_slug):
        tags = Tag.objects.all()
        return tags
