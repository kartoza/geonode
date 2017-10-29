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

from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import Unauthorized

from guardian.shortcuts import get_objects_for_user

from geonode import geoserver, qgis_server
from geonode.utils import check_ogc_backend


class GeoNodeAuthorization(DjangoAuthorization):

    """Object level API authorization based on GeoNode granular
    permission system"""

    def read_list(self, object_list, bundle):
        permitted_ids = get_objects_for_user(
            bundle.request.user,
            'base.view_resourcebase').values('id')

        return object_list.filter(id__in=permitted_ids)

    def read_detail(self, object_list, bundle):
        if 'schema' in bundle.request.path:
            return True
        return bundle.request.user.has_perm(
            'view_resourcebase',
            bundle.obj.get_self_resource())

    def create_list(self, object_list, bundle):
        # TODO implement if needed
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        return bundle.request.user.has_perm(
            'add_resourcebase',
            bundle.obj.get_self_resource())

    def update_list(self, object_list, bundle):
        # TODO implement if needed
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        return bundle.request.user.has_perm(
            'change_resourcebase',
            bundle.obj.get_self_resource())

    def delete_list(self, object_list, bundle):
        # TODO implement if needed
        raise Unauthorized()

    def delete_detail(self, object_list, bundle):
        return bundle.request.user.has_perm(
            'delete_resourcebase',
            bundle.obj.get_self_resource())


class GeoNodeStyleAuthorization(GeoNodeAuthorization):
    """Object level API authorization based on GeoNode granular
    permission system

    Style object permissions should follow it's layer permissions
    """

    def filter_by_resource_ids(self, object_list, permitted_ids):
        """Filter Style queryset by permitted resource ids."""
        if check_ogc_backend(geoserver.BACKEND_PACKAGE):
            return object_list.filter(layer_styles__id__in=permitted_ids)
        elif check_ogc_backend(qgis_server.BACKEND_PACKAGE):
            return object_list.filter(
                layer_styles__layer__id__in=permitted_ids)

    def read_list(self, object_list, bundle):
        permitted_ids = get_objects_for_user(
            bundle.request.user,
            'base.view_resourcebase').values('id')

        return self.filter_by_resource_ids(object_list, permitted_ids)

    def delete_detail(self, object_list, bundle):
        permitted_ids = get_objects_for_user(
            bundle.request.user,
            'layer.change_layer_style').values('id')

        resource_obj = bundle.obj.get_self_resource()
        return resource_obj in permitted_ids
