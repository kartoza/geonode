from django.contrib.gis.db import models
from groundwater.models import Quantity
from groundwater.models.well import GWWell


class GWGeologyLog(models.Model):
    """
    8.1.9 GW_GeologyLog
    Specialization of the OM_Observation containing the log start and end depth for
    coverages.
    For Stratigraphic logs the observedProperty will be a GeoSciML:GeologicUnit/name.
    For Lithologic logs the observedProperty will be a
    GeoSciML:GeologicUnit/composition/CompositionPart/material.
    """

    phenomenon_time = models.DateTimeField(
        null=True, blank=True, verbose_name='phenomenonTime')
    result_time = models.DateTimeField(
        null=True, blank=True, verbose_name='resultTime')
    parameter = models.TextField(null=True, blank=True)
    gw_level = models.FloatField(
        null=True, blank=True, verbose_name='gw_level')
    reference = models.TextField(
        null=True, blank=True, verbose_name='reference')
    start_depth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='startDepth',
        verbose_name='startDepth')
    end_depth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='endDepth',
        verbose_name='endDepth')
    gw_well = models.ForeignKey(
        GWWell,
        null=True, blank=True, verbose_name="gwWell", on_delete=models.SET_NULL)  # many to one to GWWell
