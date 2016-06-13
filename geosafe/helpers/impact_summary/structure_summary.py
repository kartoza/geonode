# coding=utf-8
from collections import OrderedDict

from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/18/16'


class StructureSummary(ImpactSummary):

    def total(self):
        return self.total_buildings()

    def total_buildings(self):
        return self.summary_dict().get('Total')

    def total_affected(self):
        if 'Affected buildings' in self.summary_dict().keys():
            return self.summary_dict().get('Affected buildings')
        elif 'Not affected buildings' in self.summary_dict().keys():
            not_affected = self.summary_dict().get('Not affected buildings')
            return int(self.total_buildings()) - int(not_affected)

    def breakdown_dict(self):
        ret_val = OrderedDict()
        for key, value in self.summary_dict().iteritems():
            contain_total = 'total' in key.lower()
            contain_affected = 'affected' in key.lower()
            contain_not = 'not' in key.lower()
            if contain_total or (contain_affected and not contain_not):
                continue

            ret_val[key] = int(value)
        return ret_val

    def category_css_class(self, category):
        css_class = ImpactSummary.category_css_class(category)
        if not css_class:
            if 'flood' in category.lower():
                css_class = 'hazard-category-high'
            elif 'dry' in category.lower():
                css_class = 'hazard-category-low'
            elif 'wet' in category.lower():
                css_class = 'hazard-category-medium'
            elif 'radius' in category.lower():
                css_class = 'hazard-category-high'
        return css_class
