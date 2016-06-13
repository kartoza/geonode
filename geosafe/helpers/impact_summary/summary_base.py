# coding=utf-8

import json
from collections import OrderedDict

from geonode.layers.models import Layer, LayerFile

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/17/16'


class ImpactSummary(object):

    def __init__(self, impact_layer):
        self._impact_layer = impact_layer
        self._impact_data = self.read_impact_data_json()

    @property
    def impact_layer(self):
        """

        :return: Impact Layer
        :rtype: Layer
        """
        return self._impact_layer

    @impact_layer.setter
    def impact_layer(self, impact_layer):
        self._impact_layer = impact_layer

    @property
    def impact_data(self):
        """

        :return: Impact data dictionary
        :rtype: dict
        """
        return self._impact_data

    @impact_data.setter
    def impact_data(self, value):
        self._impact_data = value

    def read_impact_data_json(self):
        """Read impact_data.json file from a given impact layer

        :return: dictionary of impact data
        :rtype: dict
        """
        try:
            json_file = self.impact_layer.upload_session.layerfile_set.get(
                file__endswith=".json")
            impact_data = json.loads(json_file.file.read())
            return impact_data
        except LayerFile.DoesNotExist:
            return {}

    def is_summary_exists(self):
        return self.impact_data or self.impact_data.get('impact summary')

    def maximum_category_value(self):
        if self.is_summary_exists():
            max_val = max([f.get('value') for f in self.summary_fields()])
            return max_val
        return 0

    def summary_fields(self):
        """convert impact data to list of key-value pair

        :return: list of dict of category and value
        """
        fields = []
        if self.is_summary_exists():
            fields = self.impact_data.get('impact summary').get('fields')

        ret_val = []
        for f in fields:
            ret_val.append({
                "category": f[0],
                "value": f[1]
            })

        return ret_val

    def summary_dict(self):
        """convert summary fields to key value pair"""
        ret_val = OrderedDict()
        for f in self.summary_fields():
            ret_val[f['category']] = f['value']

        return ret_val

    def summary_attributes(self):
        ret_val = OrderedDict()
        if self.is_summary_exists():
            attrs = self.impact_data.get('impact summary').get('attributes')
        return attrs

    def category_list(self):
        if self.is_summary_exists():
            return [f.get('category') for f in self.summary_fields()]

    def exposure_type(self):
        return self.impact_data.get('exposure')

    @classmethod
    def category_css_class(cls, category):
        """Get css-class from a given category

        :param category: category string
        :type category: str

        :return:
        """
        if 'high' in category.lower():
            return 'hazard-category-high'
        elif 'medium' in category.lower() or 'moderate' in category.lower():
            return 'hazard-category-medium'
        elif 'low' in category.lower():
            return 'hazard-category-low'
        elif 'total' in category.lower():
            return 'hazard-category-total'
        elif 'not affected' in category.lower():
            return 'hazard-category-not-affected'
        elif 'affected' in category.lower():
            return 'hazard-category-affected'
        else:
            return ''

