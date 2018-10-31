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

import errno
import logging
import os
import shutil
import socket

import requests
from celery.task import task
from django.contrib.gis.gdal import SpatialReference, CoordTransform, \
    OGRGeometry
from requests.exceptions import HTTPError

from geonode.layers.models import Layer
from geonode.layers.utils import create_thumbnail
from geonode.maps.models import Map
from geonode.qgis_server.helpers import (
    map_thumbnail_url,
    layer_thumbnail_url,
    tile_url,
    tile_cache_path)
from geonode.qgis_server.models import QGISServerLayer

logger = logging.getLogger(__name__)


@task(
    name='geonode.qgis_server.tasks.update.create_qgis_server_thumbnail',
    queue='update',
    autoretry_for=(QGISServerLayer.DoesNotExist, ),
    retry_kwargs={'max_retries': 5, 'countdown': 5})
def create_qgis_server_thumbnail(
        instance, overwrite=False, bbox=None, bbox_srid=None):
    """Task to update thumbnails.

    This task will formulate OGC url to generate thumbnail and then pass it
    to geonode

    :param instance: Resource instance, can be a layer or map
    :type instance: Layer, Map

    :param overwrite: set True to overwrite
    :type overwrite: bool

    :param bbox: Bounding box of thumbnail in 4 tuple format
        [xmin,ymin,xmax,ymax]
    :type bbox: list(float)

    :param bbox_srid: SRID of the bbox
    :type bbox_srid: basestring

    :return:
    """
    thumbnail_remote_url = None
    if not bbox_srid:
        # default bbox_srid
        bbox_srid = 'EPSG:4326'
    try:
        # to make sure it is executed after the instance saved
        if isinstance(instance, Layer):
            # check if bbox is empty
            if bbox is None:
                bbox = [
                    instance.bbox_x0,
                    instance.bbox_y0,
                    instance.bbox_x1,
                    instance.bbox_y1
                ]
                bbox_srid = instance.srid
            # set thumbnails use 4326, so we need to convert bbox accordingly
            if not bbox_srid == 'EPSG:4326':
                source_srs = SpatialReference(bbox_srid)
                target_srs = SpatialReference('EPSG:4326')
                coord_transform = CoordTransform(source_srs, target_srs)
                bound_geom = OGRGeometry.from_bbox(bbox)
                bound_geom.transform(coord_transform)
                bbox = bound_geom.extent
            thumbnail_remote_url = layer_thumbnail_url(
                instance, bbox=bbox, internal=False)
        elif isinstance(instance, Map):
            thumbnail_remote_url = map_thumbnail_url(
                instance, bbox=bbox, internal=False)
        else:
            # instance type does not have associated thumbnail
            return True
        if not thumbnail_remote_url:
            return True
        logger.debug('Create thumbnail for %s' % thumbnail_remote_url)

        if overwrite:
            # if overwrite, then delete existing thumbnail links
            instance.link_set.filter(
                resource=instance.get_self_resource(),
                name="Remote Thumbnail").delete()
            instance.link_set.filter(
                resource=instance.get_self_resource(),
                name="Thumbnail").delete()

        create_thumbnail(
            instance, thumbnail_remote_url,
            overwrite=overwrite, check_bbox=False)
        return True
    # if it is socket exception, we should raise it, because there is
    # something wrong with the url
    except socket.error as e:
        logger.error('Thumbnail url not accessed {url}'.format(
            url=thumbnail_remote_url))
        logger.exception(e)
        # reraise exception with original traceback
        raise
    except QGISServerLayer.DoesNotExist as e:
        logger.exception(e)
        # reraise exception with original traceback
        raise
    except Exception as e:
        logger.exception(e)
        return False


@task(
    name='geonode.qgis_server.tasks.update.cache_request',
    queue='update')
def cache_request(url, cache_file):
    """Cache a given url request to a file.

    On some rare occasions, QGIS Server url request is taking too long to
    complete. This could be a problem if user is requesting something like
    a tile or legend from Web interface and when it takes too long, the
    connection will reset. This case will make the request never be completed
    because the request died with user connection.

    For this kind of request, it is better to register the request as celery
    task. This will make the task to keep running, even if connection is
    reset.

    :param url: The target url to request
    :type url: str

    :param cache_file: The target file path to save the cache
    :type cache_file: str

    :return: True if succeeded
    :rtype: bool
    """
    logger.debug('Requesting url: {url}'.format(url=url))
    response = requests.get(url, stream=True)

    if not response.status_code == 200:
        # Failed to fetch request. Abort with error message
        msg = (
            'Failed to fetch requested url: {url}\n'
            'With HTTP status code: {status_code}\n'
            'Content: {content}')
        msg = msg.format(
            url=url,
            status_code=response.status_code,
            content=response.content)
        raise HTTPError(msg)

    dirname = os.path.dirname(cache_file)

    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with open(cache_file, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    del response

    return True


def tile_cache_seeder(layer, tiles_list, style='default'):
    """Generate QGIS Server tile cache.

    First, generate tiles_list using tile_coordinate_generator.

    :param layer: GeoNode layers
    :type layer: geonode.layers.models.Layer

    :param tiles_list: tiles tuples list from tile_coordinate_generator
    :type tiles_list: list(tuple)

    :return: processed tiles count
    :rtype: int
    """
    tile_count = 0
    for zoom, tile_y, tile_x in tiles_list:

        url = tile_url(
            layer, zoom, tile_x, tile_y,
            style='default', internal=True)

        tile_path = tile_cache_path(
            layer.qgis_layer.qgis_layer_name,
            zoom, tile_x, tile_y, style=style)

        result = cache_request.delay(url, tile_path)

        try:
            result.get()
            tile_count += 1
        except HTTPError:
            pass

    return tile_count
