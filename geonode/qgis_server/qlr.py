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
import codecs
import os

from lxml import etree, objectify


class QLRFile(object):
    """A helper class for QLR file."""

    def __init__(self, filename=None):
        self.path = filename
        with codecs.open(filename, encoding='utf-8') as f:
            self.root_xml = etree.fromstring(f.read())

    @property
    def layername(self):
        """Return layername"""
        return self.root_xml.findtext('.//layername')

    @property
    def srs(self):
        """Return SRS Info"""
        srs_xml = self.root_xml.find('.//spatialrefsys')
        return objectify.fromstring(
            etree.tostring(srs_xml))

    @property
    def proj4(self):
        return self.srs.proj4

    @property
    def srid(self):
        return self.srs.srid

    @property
    def authid(self):
        return self.srs.authid

    @property
    def provider(self):
        """Return driver provider."""
        return self.root_xml.findtext('.//provider')

    @property
    def type(self):
        """Return layer type (vector/raster)"""
        return self.root_xml.find('.//maplayer').get('type')

    @property
    def datasource(self):
        """Return connection datasource"""
        return self.root_xml.findtext('.//datasource')

    @property
    def extent(self):
        """Return extent in the format [xmin, ymin, xmax, ymax]"""
        extent_element = self.root_xml.find('.//extent')
        extent = objectify.fromstring(etree.tostring(extent_element))
        extent_list = [
            extent.xmin.text,
            extent.ymin.text,
            extent.xmax.text,
            extent.ymax.text
        ]
        # convert to float
        extent_list = [float(f) for f in extent_list]
        return extent_list


def is_qlr(filename):
    """Check extension and returns true if QLR file.

    :param filename: Layer param
    :type filename: basestring

    :return: True if QLR file
    :rtype: bool
    """
    base, ext = os.path.splitext(filename)
    if ext.lower() == '.qlr':
        return True
    return False


def populate_info_from_qlr(layer_obj, qlr_obj):
    """Populate known info from QLR to layer object.

    :param layer_obj: Layer object
    :type layer_obj: geonode.layers.models.Layer

    :param qlr_obj: QLR object
    :type qlr_obj: QLRFile

    :return: Layer object and changed kwargs
    :rtype: (geonode.layers.models.Layer, dict)
    """
    bbox_qlr = qlr_obj.extent
    srid = qlr_obj.authid

    bbox_x0, bbox_y0, bbox_x1, bbox_y1 = bbox_qlr

    # update bounds info
    layer_obj.srid = srid
    layer_obj.bbox_x0 = bbox_x0
    layer_obj.bbox_y0 = bbox_y0
    layer_obj.bbox_x1 = bbox_x1
    layer_obj.bbox_y1 = bbox_y1

    if qlr_obj.type.lower() == 'vector':
        layer_obj.storeType = 'dataStore'
    elif qlr_obj.type.lower() == 'raster':
        layer_obj.storeType = 'coverageStore'

    return layer_obj, {
        'srid': srid,
        'bbox_x0': bbox_x0,
        'bbox_x1': bbox_x1,
        'bbox_y0': bbox_y0,
        'bbox_y1': bbox_y1,
        'storeType': layer_obj.storeType
    }
