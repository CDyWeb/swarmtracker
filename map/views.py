from django.shortcuts import render
from django.views import View

from swarm import settings
from swarm.models import SwarmUser


class MapView(View):
    def get(self, request):
        return render(request, 'map.html', context={
            'map_key': settings.GOOGLE_API_KEY,
            'catchers': SwarmUser.objects.all()
        })
