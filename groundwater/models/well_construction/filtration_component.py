from django.contrib.gis.db import models
from groundwater.models import GWTerm, Quantity
from groundwater.models.well_construction import ConstructionComponent


class FiltrationMaterialTerm(GWTerm):
    """
    Material used in the filtration device. E.g. gravel,
    pit run, silica sand, washed sand, crushed rock, etc.
    """
    pass


class FiltrationComponent(models.Model):
    """
    8.1.8 FiltrationComponent
    Material used to filter the fluid in a borehole or well.
    """

    filter_grain_size = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="filterGrainSize",
        help_text="Size of the particles of the filtration material.")

    filter_material = models.ForeignKey(
        FiltrationMaterialTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="FiltrationMaterialTerm",
        help_text="Material used in the filtration device. E.g. gravel,"
                  "pit run, silica sand, washed sand, crushed rock, etc.")

    # TODO:
    #   need to ask about this construction component is
    #   just 1 for filtration or many?
    construction_component = models.ForeignKey(
        ConstructionComponent, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="ConstructionComponent",
        help_text="A filtration part is a type of construction component")
