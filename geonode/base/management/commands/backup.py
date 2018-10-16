# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 OSGeo
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
from geonode import geoserver, qgis_server
from geonode.utils import check_ogc_backend

if check_ogc_backend(geoserver.BACKEND_PACKAGE):

    from geonode.base.management.commands.backup_geoserver import *  # noqa

elif check_ogc_backend(qgis_server.BACKEND_PACKAGE):

    from geonode.qgis_server.management.commands.\
        backup_qgis_server import *  # noqa
