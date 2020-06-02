from django.contrib import admin

from swarm.models import SwarmUser


@admin.register(SwarmUser)
class SwarmUserAdmin(admin.ModelAdmin):
    pass
