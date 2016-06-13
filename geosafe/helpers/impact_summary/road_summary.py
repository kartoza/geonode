# coding=utf-8
from collections import OrderedDict

from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '6/13/16'


class RoadSummary(ImpactSummary):

    def total(self):
        return self.total_roads()

    def total_roads(self):
        for idx, val in enumerate(self.summary_attributes()):
            if 'total' in val.lower():
                if self.is_summary_exists():
                    return int(self.impact_data.get('impact summary').get(
                        'fields')[0][idx])
        return 0

    def total_affected(self):
        lowercase_keys = [k.lower() for k in self.summary_attributes()]
        for idx, val in enumerate(lowercase_keys):
            if 'flooded' in val or 'closed' in val:
                return int(self.impact_data.get('impact summary').get(
                    'fields')[0][idx])
        return 0

    def breakdown_dict(self):
        ret_val = OrderedDict()
        for idx, key in enumerate(self.summary_attributes()):
            contain_total = 'total' in key.lower()
            contain_affected = 'affected' in key.lower()
            contain_not = 'not' in key.lower()
            contain_unaffected = 'unaffected' in key.lower()
            if (contain_total or
                    (contain_affected and
                         not contain_not and
                         not contain_unaffected)):
                continue

            ret_val[key] = int(self.impact_data.get('impact summary').get(
                'fields')[0][idx])
        return ret_val

    def category_css_class(self, category):
        css_class = ImpactSummary.category_css_class(category)
        if not css_class:
            if 'closed' in category.lower():
                css_class = 'hazard-category-high'
            elif 'flooded' in category.lower():
                css_class = 'hazard-category-high'
        return css_class
