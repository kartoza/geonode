from django.contrib.gis.db import models
from groundwater.models.well_construction import Borehole
from groundwater.models import Quantity


class WellStatusTypeTerm(models.Model):
    """
    Status of the well, Can be new, unfinished,
    reconditioned, deepened, not in use, standby,
    unknown, abandoned dry, abandoned
    insufficient, abandoned quality. (gwml1)
    """
    name = models.TextField()


class GWWell(models.Model):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""

    gw_well_name = models.TextField(null=False, blank=False, verbose_name="gwWellName")
    gw_well_location = models.PointField(null=False, blank=False, verbose_name="gwWellLocation")
    gw_well_contribution_zone = models.GeometryField(
        null=True, blank=True, verbose_name="gwWellContributionZone")
    gw_well_construction = models.ForeignKey(
        Borehole, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellConstruction")
    gw_well_total_length = models.FloatField(
        null=True, blank=True,
        verbose_name="gwWellTotalLength")
    gw_well_status = models.ForeignKey(
        WellStatusTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellStatus")
    gw_well_static_water_depth = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellStaticWaterDepth")
