from django.contrib.gis.db import models
from groundwater.models import Quantity


class Borehole(models.Model):
    """
    8.1.2 Borehole
    General term for a hole drilled in the ground for various purposes such extraction of a
    core, release of fluid, etc.
    """

    bhole_date_of_drilling = models.DateField(
        null=True,
        verbose_name="bholeDateOfDrilling",
        help_text="Date of drilling.")
    bhole_nominal_diameter = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="bholeNominalDiameter",
        help_text="Diameter of the borehole.")
