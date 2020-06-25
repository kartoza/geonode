from django.contrib import admin
from .models import GW_Well, GW_GeologyLog


class GW_GeologyLogAdmin(admin.ModelAdmin):
    list_display = ('phenomenonTime', 'resultTime', 'parameter', 'gw_level', 'reference', 'startDepth', 'endDepth')


admin.site.register(GW_Well)
admin.site.register(GW_GeologyLog, GW_GeologyLogAdmin)
