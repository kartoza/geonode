from django.contrib import admin
from groundwater.models.well import GWWell, GWGeologyLog


class GWGeologyLogAdmin(admin.ModelAdmin):
    list_display = ('phenomenon_time', 'result_time', 'parameter', 'gw_level', 'reference', 'start_depth', 'end_depth')


admin.site.register(GWWell)
admin.site.register(GWGeologyLog, GWGeologyLogAdmin)
