from django.shortcuts import render

# Create your views here.
from django.views import View

from report.models import SwarmReport


class CatchView(View):
    def get(self, request):
        return render(request, 'catch.html', context={
            'swarms': SwarmReport.objects.filter().only('id', 'created_at', 'latitude', 'longitude', 'location_reverse').order_by('-created_at')
        })
