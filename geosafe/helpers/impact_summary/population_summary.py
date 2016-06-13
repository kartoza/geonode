# coding=utf-8
from collections import OrderedDict

from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/18/16'


class PopulationSummary(ImpactSummary):

    def total(self):
        return self.total_populations()

    def total_populations(self):
        return self.summary_dict().get('Total population')

    def total_affected(self):
        if 'Total affected population' in self.summary_dict().keys():
            return int(self.summary_dict().get('Total affected population'))
        return 0

    def breakdown_dict(self):
        ret_val = OrderedDict()
        for key, value in self.summary_dict().iteritems():
            contain_total = 'total' in key.lower()
            contain_affected = 'affected' in key.lower()
            contain_not = 'not' in key.lower()
            contain_unaffected = 'unaffected' in key.lower()
            if (contain_total or
                    (contain_affected and
                         not contain_not and
                         not contain_unaffected)):
                continue

            ret_val[key] = int(value)
        return ret_val

    def category_css_class(self, category):
        css_class = ImpactSummary.category_css_class(category)
        if not css_class:
            if 'people' in category.lower():
                css_class = 'hazard-category-high'
            elif 'fatalities' in category.lower():
                css_class = 'hazard-category-high'
            elif 'displaced' in category.lower():
                css_class = 'hazard-category-high'
            elif 'affected' in category.lower():
                css_class = 'hazard-category-high'
            elif 'floodprone' in category.lower():
                css_class = 'hazard-category-high'
            elif 'radius' in category.lower():
                css_class = 'hazard-category-high'
        return css_class
