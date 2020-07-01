from django.contrib.gis.db import models
from groundwater.models import GWTerm
from groundwater.models import Quantity


class CasingMaterialTerm(GWTerm):
    """
    Material in which the casing is made. E.g. metal,
    steel, iron, concrete, wood, brick, plastic, teflon,
    PVC, ABS, fibreglass, etc.
    """
    pass


class CasingCoatingTerm(GWTerm):
    """
    Coating applied to the casing. E.g. galvanized,
    stainless, mild, low carbon, copper bearing,
    black, etc.
    """
    pass


class CasingFormTerm(GWTerm):
    """
    Form of material used in the casing. E.g.
    """
    pass


class CasingComponent(models.Model):
    """
    8.1.4 CasingComponent
    A single part of a borehole casing.
    """
    casing_material = models.ForeignKey(
        CasingMaterialTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='casingMaterial',
        related_name='casing_material',
        help_text="Material in which the casing is made. E.g. metal, "
                  "steel, iron, concrete, wood, brick, plastic, teflon,"
                  "PVC, ABS, fibreglass, etc.")
    casing_coating = models.ForeignKey(
        CasingMaterialTerm, null=True, blank=True,
        related_name='casing_coating',
        on_delete=models.SET_NULL, verbose_name='casingCoating',
        help_text="Coating applied to the casing. E.g. galvanized,"
                  "stainless, mild, low carbon, copper bearing,"
                  "black, etc.")
    casing_form = models.ForeignKey(
        CasingFormTerm, null=True, blank=True,
        related_name='casing_form',
        on_delete=models.SET_NULL, verbose_name='casingForm',
        help_text="Form of material used in the casing. E.g.")
    casing_internal_diameter = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='casing_internal_diameter',
        on_delete=models.SET_NULL, verbose_name='casingInternalDiameter',
        help_text="Internal diameter of the casing.")
    casing_external_diameter = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='casing_external_diameter',
        on_delete=models.SET_NULL, verbose_name='casingExternalDiameter',
        help_text="External diameter of the casing.")
    casing_wall_thickness = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='casing_wall_thickness',
        on_delete=models.SET_NULL, verbose_name='casingWallThickness',
        help_text="Thickness of the wall of the casing.")
