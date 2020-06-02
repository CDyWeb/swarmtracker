from django.contrib import admin

from report.models import SwarmReport


@admin.register(SwarmReport)
class SwarmReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'created_at', 'reporter', 'name')
