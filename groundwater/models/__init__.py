from django.contrib.gis.db import models


class Quantity(models.Model):
    """ Model to define quantity. """
    unit = models.TextField(
        null=True, blank=True)
    value = models.FloatField(
        null=True, blank=True)
