# coding=utf-8
"""Urls for igrac apps."""

from django.conf.urls import url
from .views import CsvUploadView


urlpatterns = [
    url(r'^well_upload/$',
        view=CsvUploadView.as_view(),
        name='csv_upload_view'),
]
