# coding=utf-8
from django.core.management.base import BaseCommand
from geonode.maps.models import Map
from ...models.map_slug import MapSlugMapping


class Command(BaseCommand):
    """Update all map to have map slugs.
    """
    args = ''
    help = 'Update all map to have map slugs.'

    def handle(self, *args, **options):
        """Implementation for command.
        :param args:  Not used
        :param options: Not used

        """

        print('--------------------------------------------------------------')
        print('Mapping existing maps with new slugs.')
        print('--------------------------------------------------------------')

        map_with_slug = MapSlugMapping.objects.all().values_list('map__id', flat=True)
        maps = Map.objects.exclude(id__in=map_with_slug)
        for map in maps:
            map_obj = MapSlugMapping.objects.create(map=map)

        print('--------------------------------------------------------------')
        print('{} existing maps have been updated with new slugs.'.format(maps.count()))
        print('--------------------------------------------------------------')
