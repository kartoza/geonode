from django.contrib.gis.db import models


class Quantity(models.Model):
    """Model to define quantity."""

    unit = models.TextField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)

    class Meta:
        managed = True
        # db_table = 'groundwater\".\"quantity'


class Borehole(models.Model):
    """Model to define groundwater borehole."""

    id = models.AutoField(primary_key=True)
    bholeDateOfDrilling = models.DateField(null=True)
    bholeNominalDiameter = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        # db_table = 'groundwater\".\"borehole'


class WellStatusTypeTerm(models.Model):
    """Model to define groundwater Well Status Type."""

    name = models.TextField()

    class Meta:
        managed = True
        # db_table = 'groundwater\".\"wellstatustypeterm'


class GW_GeologyLog(models.Model):
    """Model to define groundwater geology log."""

    phenomenonTime = models.DateTimeField(null=True, blank=True)
    resultTime = models.DateTimeField(null=True, blank=True)
    parameter = models.TextField(null=True, blank=True)
    gw_level = models.FloatField(null=True, blank=True)
    reference = models.TextField(null=True, blank=True)
    startDepth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.CASCADE, related_name='startDepth')
    endDepth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.CASCADE, related_name='endDepth')

    class Meta:
        managed = True
        # db_table = 'groundwater\".\"gw_geologylog'


class GW_Well(models.Model):
    """Model to define groundwater well."""

    gwwellname = models.TextField(null=False, blank=False)
    gwwelllocation = models.PointField(null=False, blank=False)
    gwwellcontributionzone = models.GeometryField(null=True, blank=True)
    gwwellconstruction = models.ForeignKey(
        Borehole, null=True, blank=True, on_delete=models.CASCADE)
    gwwelltotallength = models.FloatField(null=True, blank=True)
    gwwellstatus = models.ForeignKey(
        WellStatusTypeTerm, null=True, blank=True, on_delete=models.CASCADE)
    gwwellstaticwaterdepth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.CASCADE)
    gwwellgeology = models.ManyToManyField(GW_GeologyLog, null=True, blank=True)

    class Meta:
        managed = True
        # db_table = 'groundwater\".\"gw_well'

