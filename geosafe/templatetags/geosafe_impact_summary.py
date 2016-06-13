# coding=utf-8
"""Custom template filters used in impact summary generations"""
from django import template

from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/18/16'


register = template.Library()


@register.filter
def category_css_class(value, arg):
    """

    :param value: the category (High hazard, medium hazard, etc)
    :return:
    """
    return value.category_css_class(arg)

