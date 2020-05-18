from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user
from swarm.models import SwarmUser as User
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.views import View
from report.models import SwarmReport
import requests


class ReportForm(ModelForm):
    def full_clean(self):
        if 'latitude' in self.data and 'longitude' in self.data:
            self.data['latitude'] = round(Decimal(self.data['latitude']), 6)
            self.data['longitude'] = round(Decimal(self.data['longitude']), 6)
        return super().full_clean()

    class Meta:
        fields = '__all__'
        model = SwarmReport


class ReportView(View):
    def get(self, request):
        user: User = get_user(request)
        report = SwarmReport(
            name=f'{user.first_name} {user.last_name}' if user and user.is_authenticated else '',
            email=user.email if user and user.is_authenticated else '',
            location='',
        )
        return render(request, 'report.html', context={
            'recaptcha_key': settings.RECAPTCHA_KEY,
            'report': report
        })

    def post(self, request):
        posted_data = request.POST.dict()
        if 'recaptcha' not in posted_data:
            return redirect(request.path)

        try:
            resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': settings.RECAPTCHA_SECRET,
                'response': posted_data.get('recaptcha'),
            })
            resp.raise_for_status()
            if not resp.json().get('success'):
                return redirect(request.path)
        except:
            return redirect(request.path)

        form = ReportForm(data=posted_data)
        if form.is_valid():
            user = get_user(request)
            if user.is_authenticated:
                form.instance.reporter = user
            swarm: SwarmReport = form.save()
            request.session['report_id'] = str(swarm.id)

            try:
                map_key = settings.MAPQUESTAPI_KEY
                resp = requests.get(
                    f'http://open.mapquestapi.com/geocoding/v1/reverse?'
                    f'key={map_key}&location={swarm.latitude},{swarm.longitude}'
                )
                resp.raise_for_status()
                swarm.location_reverse = resp.json().get('results', [{}])[0].get('locations', [{}])[0]
                swarm.save()
            except:
                pass

            return redirect('report-done')

        errors = []
        for f, error in form.errors.items():
            errors.append(f'{f}: ' + ', '.join(error))
        return render(request, 'report.html', context={
            'recaptcha_key': settings.RECAPTCHA_KEY,
            'report': form.instance,
            'errors': errors
        })


class ReportDoneView(View):
    def get(self, request):
        try:
            uuid = request.session.get('report_id')
            swarm = SwarmReport.objects.get(pk=uuid)
        except Exception:
            return redirect('report-swarm')

        return render(request, 'report-done.html', context={
            'swarm': swarm,
        })


class ReportDetailsView(View):
    def get(self, request, uuid):
        try:
            swarm = SwarmReport.objects.get(pk=uuid)
        except Exception:
            return render(request, '404.html', status=404)

        return render(request, 'swarm.html', context={
            'swarm': swarm,
        })
