from django.contrib.gis.db import models


class SealingTypeTerm(models.Model):
    """
    Type of sealing. E.g. annular sealing, plugging, etc.
    """
    name = models.CharField(max_length=256)
    description = models.TextField()


class SealingMaterialTerm(models.Model):
    """
    Material used in the sealing component of a
    water well. E.g. formation packer, welded ring,
    shale trap, drive shoe, driven casing, etc.
    """
    name = models.CharField(max_length=256)
    description = models.TextField()


class SealingComponent(models.Model):
    """
    8.1.15 SealingComponent
    A material used for sealing the construction of a borehole or well.
    """
    sealing_material = models.ForeignKey(
        SealingMaterialTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='sealingMaterial')
    sealing_type = models.ForeignKey(
        SealingTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='sealingType')
