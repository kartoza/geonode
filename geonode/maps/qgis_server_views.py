# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
import json
import requests

from django.conf import settings
from django.views.generic import CreateView, DetailView
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from geonode.maps.views import _resolve_map, _PERMISSION_MSG_VIEW, \
    snapshot_config

from geonode.maps.models import Map, MapLayer
from geonode.layers.models import Layer


class MapCreateView(CreateView):
    model = Map
    fields = '__all__'
    template_name = 'leaflet_maps/map_view.html'
    context_object_name = 'map'

    def get_context_data(self, **kwargs):
        # list all required layers
        layers = Layer.objects.all()
        context = {
            'create': True,
            'layers': layers
        }
        return context

    def get_success_url(self):
        pass

    def get_form_kwargs(self):
        kwargs = super(MapCreateView, self).get_form_kwargs()
        return kwargs


class MapDetailView(DetailView):
    model = Map
    template_name = 'leaflet_maps/map_view.html'
    context_object_name = 'map'

    def get_context_data(self, **kwargs):
        """Prepare context data."""

        mapid = self.kwargs.get('mapid')
        snapshot = self.kwargs.get('snapshot')
        request = self.request

        map_obj = _resolve_map(
            request, mapid, 'base.view_resourcebase', _PERMISSION_MSG_VIEW)

        if 'access_token' in request.session:
            access_token = request.session['access_token']
        else:
            access_token = None

        if snapshot is None:
            config = map_obj.viewer_json(request.user, access_token)
        else:
            config = snapshot_config(snapshot, map_obj, request.user,
                                     access_token)
        # list all required layers
        layers = Layer.objects.all()
        map_layers = MapLayer.objects.filter(
            map_id=mapid).order_by('stack_order')
        context = {
            'config': json.dumps(config),
            'create': False,
            'layers': layers,
            'map': map_obj,
            'map_layers': map_layers,
            'preview': getattr(
                settings,
                'LAYER_PREVIEW_LIBRARY',
                '')
        }
        return context

    def get_object(self):
        return Map.objects.get(id=self.kwargs.get("mapid"))


def map_download_qlr(request, mapid):
    """Download QLR file to open the maps' layer in QGIS desktop.

    :param request: The request from the frontend.
    :type request: HttpRequest

    :param mapid: The id of the map.
    :type mapid: String

    :return: QLR file.
    """

    map_obj = _resolve_map(request,
                           mapid,
                           'base.view_resourcebase',
                           _PERMISSION_MSG_VIEW)

    def perm_filter(layer):
        return request.user.has_perm(
            'base.view_resourcebase',
            obj=layer.get_self_resource())

    mapJson = map_obj.json(perm_filter)

    # we need to remove duplicate layers
    j_map = json.loads(mapJson)
    j_layers = j_map["layers"]
    for j_layer in j_layers:
        if j_layer["service"] is None:
            j_layers.remove(j_layer)
            continue
        if (len([l for l in j_layers if l == j_layer])) > 1:
            j_layers.remove(j_layer)

    map_layers = []
    for layer in j_layers:
        layer_name = layer["name"].split(":")[1]
        ogc_url = reverse('qgis_server:layer-request',
                          kwargs={'layername': layer_name})
        url = settings.SITEURL + ogc_url.replace("/", "", 1)

        map_layers.append({
            'type': 'raster',
            'display': layer_name,
            'driver': 'wms',
            'crs': 'EPSG:4326',
            'format': 'image/png',
            'styles': '',
            'layers': layer_name,
            'url': url
        })

    json_layers = json.dumps(map_layers)
    url_server = settings.QGIS_SERVER_URL \
        + '?SERVICE=LAYERDEFINITIONS&LAYERS=' + json_layers
    fwd_request = requests.get(url_server)
    response = HttpResponse(
        fwd_request.content, content_type="application/xml",
        status=fwd_request.status_code)
    response['Content-Disposition'] = 'attachment; filename=%s' \
                                      % map_obj.title + '.qlr'

    return response


class MapEmbedView(DetailView):
        model = Map
        template_name = 'leaflet_maps/map_detail.html'
        context_object_name = 'map'

        def get_context_data(self, **kwargs):
            """Prepare context data."""

            mapid = self.kwargs.get('mapid')
            snapshot = self.kwargs.get('snapshot')
            request = self.request

            map_obj = _resolve_map(
                request, mapid, 'base.view_resourcebase', _PERMISSION_MSG_VIEW)

            if 'access_token' in request.session:
                access_token = request.session['access_token']
            else:
                access_token = None

            if snapshot is None:
                config = map_obj.viewer_json(request.user, access_token)
            else:
                config = snapshot_config(snapshot, map_obj, request.user,
                                         access_token)
            # list all required layers
            layers = Layer.objects.all()
            map_layers = MapLayer.objects.filter(
                map_id=mapid).order_by('stack_order')
            context = {
                'config': json.dumps(config),
                'create': False,
                'layers': layers,
                'resource': map_obj,
                'map_layers': map_layers,
                'preview': getattr(
                    settings,
                    'LAYER_PREVIEW_LIBRARY',
                    '')
            }
            return context

        def get_object(self):
            return Map.objects.get(id=self.kwargs.get("mapid"))
