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

"""
Related documentation/reference

https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

"""
import errno
import shutil
from urllib2 import HTTPError

from django.conf import settings
from django.core.management import BaseCommand
from tqdm import tqdm

from geonode.layers.models import Layer
from geonode.qgis_server.helpers import (
    transform_layer_bbox, legend_url,
    legend_cache_path, tile_coordinate_generator)
from geonode.qgis_server.tasks.update import (
    cache_request,
    create_qgis_server_thumbnail,
    tile_cache_seeder)

QGIS_SERVER_CONFIG = settings.QGIS_SERVER_CONFIG if \
    hasattr(settings, 'QGIS_SERVER_CONFIG') else None


class Command(BaseCommand):

    help = 'Seed a layer with tile cache using QGIS Server'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'layer_name',
            type=str,
            help='GeoNode layer name.')

        # Optional arguments
        parser.add_argument(
            '-z',
            '--zoom-level',
            action='store',
            dest='zoom_level',
            type=int,
            nargs=2,
            default=[10, 12],
            help='Inclusive range of zoom level to seed. '
                 'Valid value from 0 to 20. '
                 'Separate with comma'
                 'Example: -z 5 10'
        )
        parser.add_argument(
            '-t',
            '--thumbnail-extent',
            action='store',
            dest='thumbnail_extent',
            type=float,
            nargs=4,
            help='BBOX range for thumbnail regeneration.'
                 'Format -t x0 x1 y0 y1 .'
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            dest='noinput',
            help='Auto accept all questions.'
        )

    def calculating_number_of_tiles(self, layer, zoom_level):
        """Sub task: calculate number of tiles"""
        print 'Calculating number of tiles'

        tiles_list, tile_count = tile_coordinate_generator(
            layer, zoom_level[0], zoom_level[1])

        print 'Number of tiles predicted: {}'.format(tile_count)
        return tiles_list, tile_count

    def cleanup(self, layer):
        """Sub task: Clean cache files."""
        print 'Cleanup cache files.'

        try:
            shutil.rmtree(layer.qgis_layer.cache_path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                print e
                raise

    def generate_tiles(self, layer, tile_count, tiles_list):
        print 'Prepare to generate tiles.'

        iterator = tqdm(tiles_list, unit='tile', total=tile_count)
        tile_count = tile_cache_seeder(layer, iterator)

        print 'Seeding done.'

        return tile_count

    def generate_thumbnail(self, layer, thumbnail_extent):
        print 'Generating thumbnail.'
        if thumbnail_extent:
            x0, y0, x1, y1 = thumbnail_extent
        else:
            x0, y0, x1, y1 = transform_layer_bbox(layer, 4326)
        result = create_qgis_server_thumbnail.delay(
            layer, overwrite=True, bbox=[x0, y0, x1, y1],
            bbox_srid='EPSG:4326')
        try:
            result.get()
            print 'Successfully generated thumbnail.'
        except HTTPError as e:
            print e

    def generate_legend(self, layer):
        print 'Generating legend.'
        url = legend_url(layer, False, style='default', internal=True)
        legend_path = legend_cache_path(
            layer.qgis_layer.qgis_layer_name, style='default')
        result = cache_request.delay(url, legend_path)
        try:
            result.get()
            print 'Successfully generated legend.'
        except HTTPError as e:
            print e

    def handle(self, *args, **options):
        zoom_level = options.get('zoom_level')
        thumbnail_extent = options.get('thumbnail_extent')
        layer_name = options.get('layer_name')
        noinput = options.get('noinput')

        try:
            layer = (Layer.objects.get(name=layer_name)
                     or Layer.objects.get(alternate=layer_name))
        except Layer.DoesNotExist:
            print 'Specified layer: "{}" not found'.format(layer_name)
            raise

        print 'Layer found.'

        tiles_list, tile_count = self.calculating_number_of_tiles(
            layer, zoom_level)

        ans = 'y'
        if not noinput:
            ans = raw_input('Proceed (Y/n)? ')

        if ans.lower() == 'n':
            print 'Command canceled.'
            return

        self.cleanup(layer)

        self.generate_legend(layer)

        self.generate_thumbnail(layer, thumbnail_extent)

        tile_count = self.generate_tiles(layer, tile_count, tiles_list)

        print 'Processed {} tiles.'.format(tile_count)
