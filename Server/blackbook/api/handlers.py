from piston.handler import BaseHandler
from piston.utils import rc, validate, FormValidationError

from django.db.models import Q
from django.contrib.gis.measure import D

from iconography.models import Tag, LightMap
from api.forms import PaginationForm, APISearchForm, GeoForm

from django.core.paginator import Paginator, EmptyPage, InvalidPage

from piston.handler import BaseHandler

##
# Handler Base
###

class PandaBaseHandler(BaseHandler):
    def paginate(self, queryset, page=1, objects_per_page=10):
        paginator = Paginator(queryset, objects_per_page)

        try:
            page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        return page

    def get_response_dict(self, ret):
        return { 'result': ret, 'error': None }

    def _get_pagination_dict(self, page):
        if page:
            return {
                'total_objects': page.paginator.count,
                'objects_per_page': page.paginator.per_page,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
                'current_page': page.number,
                'num_pages': page.paginator.num_pages
            }

        return None

    def get_paginated_response_dict(self, page, ret):
        ret = self.get_response_dict(ret)
        ret['paginator'] = self._get_pagination_dict(page)
        return ret


class BlackbookBaseHandler(PandaBaseHandler):
    def tag_to_dict(self, tag):
        return {
            'id': tag.id,
            'name': tag.name,
            'icon': tag.icon,
            'asset': tag.asset,
            'radius': tag.radius,
            'location': tag.location,
            'latitude': tag.latitude,
            'longitude': tag.longitude,
            'expires': tag.expires,
            'created': tag.created,
            'modified': tag.modified,
        }

    def lightmap_to_dict(self, lightmap):
        return {
            'id': lightmap.id,
            'name': lightmap.name,
            'map': lightmap.map,
            'radius': lightmap.radius,
            'location': lightmap.location,
            'latitude': lightmap.latitude,
            'longitude': lightmap.longitude,
            'expires': lightmap.expires,
            'created': lightmap.created,
            'modified': lightmap.modified,
        }

###
# Helper for Geo Queries
##
def point(longitude, latitude):
    return fromstr(
        'POINT(%s %s)' % (longitude, latitude,), srid=settings.DEFAULT_SRID
    )

###
# Handlers
##

class TagHandler(BlackbookBaseHandler):
    allowed_methods = ('GET', 'POST')

    @validate(PaginationForm, 'GET')
    def read(self, request):
        pagination_form = request.form
        queryset = Tag.objects.all()

        page = self.paginate(
            queryset,
            page=pagination_form.cleaned_data['page'],
            objects_per_page=pagination_form.get_limit(25)
        )

        tags = list(page.object_list)

        return self.get_paginated_response_dict(page, [
            self.tag_to_dict(tag,) \
                for tag in tags
        ])

class TagSearchHandler(BlackbookBaseHandler):
    allowed_methods = ('GET')

    @validate(PaginationForm, 'GET')
    def read(self, request):
        pagination_form = request.form
        geo_form = GeoForm(request.GET)
        search_form = APISearchForm(request.GET)

        queryset = Tag.objects.all()

        if geo_form.is_valid():
            queryset = queryset.filter(venue__coordinates__distance_lte=(
                point(
                    geo_form.cleaned_data['longitude'],
                    geo_form.cleaned_data['latitude'],
                ),
                D(mi=geo_form.get_radius(max_radius=100))
            ))
        #elif not search_form.is_valid():
        #    raise FormValidationError(geo_form)

        if search_form.is_valid():
            search_query = ' '.join(search_form.cleaned_data['query'])
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(lineup_denorm__icontains=search_query) |
                Q(venue__name__icontains=search_query)
            )

        page = self.paginate(
            queryset,
            page=pagination_form.cleaned_data['page'],
            objects_per_page=pagination_form.get_limit(25)
        )

        tags = list(page.object_list)

        return self.get_paginated_response_dict(page, [
            self.tag_to_dict(tags,) \
                for tag in tags
        ])

class LightMapHandler(BlackbookBaseHandler):
    allowed_methods = ('GET', 'POST')

    @validate(PaginationForm, 'GET')
    def read(self, request):
        pagination_form = request.form
        geo_form = GeoForm(request.GET)
        search_form = APISearchForm(request.GET)

        queryset = LightMap.objects.all()

        if geo_form.is_valid():
            queryset = queryset.filter(venue__coordinates__distance_lte=(
                point(
                    geo_form.cleaned_data['longitude'],
                    geo_form.cleaned_data['latitude'],
                ),
                D(mi=geo_form.get_radius(max_radius=100))
            ))
        elif not search_form.is_valid():
            raise FormValidationError(geo_form)

        if search_form.is_valid():
            search_query = ' '.join(search_form.cleaned_data['query'])
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(lineup_denorm__icontains=search_query) |
                Q(venue__name__icontains=search_query)
            )

        page = self.paginate(
            queryset,
            page=pagination_form.cleaned_data['page'],
            objects_per_page=pagination_form.get_limit(25)
        )

        tags = list(page.object_list)

        return self.get_paginated_response_dict(page, [
            self.tag_to_dict(tags,) \
                for tag in tags
        ])
