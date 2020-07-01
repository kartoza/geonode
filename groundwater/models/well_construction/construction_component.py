from django.contrib.gis.db import models
from groundwater.models import Quantity


class ConstructionComponent(models.Model):
    """
    8.1.5 ConstructionComponent
    Elements used in borehole construction.
    """

    from_component = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='construction_component_from',
        db_column='from',
        help_text="Position of the top "
                  "(nearest to the borehole start) of the component.")
    to_component = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='construction_component_to',
        db_column='to',
        help_text="Position of the bottom "
                  "(farthest to the borehole start) of the component.")
