# coding=utf-8

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from geonode.maps.models import Map
from ..utilities import STOP_WORDS, check_slug


class MapSlugMapping(models.Model):
    """Model to define slug for each map."""

    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        """Overwrite save method.

        :param args:
        :param kwargs:
        """
        if not self.pk:
            words = self.map.title.split()
            filtered_words = [t for t in words if t.lower() not in STOP_WORDS]
            # unidecode() represents special characters (unicode data) in ASCII
            new_list = ' '.join(filtered_words)
            new_slug = slugify(new_list)[:50]
            new_slug = \
                check_slug(MapSlugMapping.objects.all(), new_slug)
            self.slug = new_slug
        super(MapSlugMapping, self).save(*args, **kwargs)


@receiver(post_save, sender=Map)
def create_map_slug(sender, instance, **kwargs):
    map, created = MapSlugMapping.objects.get_or_create(map=instance)
