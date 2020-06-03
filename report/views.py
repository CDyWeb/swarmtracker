import json
from decimal import Decimal

from cloudinary.forms import CloudinaryJsFileField
from django.conf import settings
from django.contrib.auth import get_user
from django.http import HttpResponse

from swarm import RecaptchaView
from swarm.models import SwarmUser as User
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.views import View
from report.models import SwarmReport, SwarmPhoto, SwarmNote
import requests


class PhotoForm(ModelForm):
    class Meta:
        model = SwarmPhoto
        fields = '__all__'


class PhotoDirectForm(PhotoForm):
    image = CloudinaryJsFileField()


class ReportForm(ModelForm):
    def full_clean(self):
        if 'latitude' in self.data and 'longitude' in self.data:
            self.data['latitude'] = round(Decimal(self.data['latitude']), 6)
            self.data['longitude'] = round(Decimal(self.data['longitude']), 6)
        return super().full_clean()

    class Meta:
        fields = '__all__'
        model = SwarmReport

class ReportView(RecaptchaView):
    def get(self, request):
        user: User = get_user(request)
        report = SwarmReport(
            name=f'{user.first_name} {user.last_name}' if user and user.is_authenticated else '',
            email=user.email if user and user.is_authenticated else '',
            location='',
        )
        return render(request, 'report.html', context={
            'map_key': settings.GOOGLE_API_KEY,
            'recaptcha_key': settings.RECAPTCHA_KEY,
            'report': report
        })

    def post(self, request):
        form = ReportForm(data=request.POST.dict())
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

        return render(request, 'report.html', context={
            'map_key': settings.GOOGLE_API_KEY,
            'recaptcha_key': settings.RECAPTCHA_KEY,
            'report': form.instance,
            'errors': [f'{f}: ' + ', '.join(error) if f != '__all__' else ', '.join(error) for f, error in form.errors.items()]
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


def direct_upload_complete(request, uuid):
    form = PhotoDirectForm(request.POST.dict())
    if form.is_valid():
        # Create a model instance for uploaded image using the provided data
        instance: SwarmPhoto = form.save(commit=False)
        instance.swarm = SwarmReport.objects.get(pk=uuid)
        instance.save()
        ret = dict(photo_id=instance.id)
    else:
        ret = dict(errors=form.errors)

    return HttpResponse(json.dumps(ret), content_type='application/json')


class ReportDetailsView(View):
    def get(self, request, uuid):
        try:
            swarm = SwarmReport.objects.get(pk=uuid)
        except Exception:
            return render(request, '404.html', status=404)

        return render(request, 'swarm.html', context={
            'swarm': swarm,
            'notes': SwarmNote.objects.filter(swarm=swarm).order_by('-create_time'),
            'pictures': SwarmPhoto.objects.filter(swarm=swarm).order_by('create_time')
        })

    def post(self, request, uuid):
        author = get_user(request)
        SwarmNote.objects.create(
            swarm=SwarmReport.objects.get(pk=uuid),
            author=author if author.is_authenticated else None,
            note=request.POST.dict().get('note')
        )
        return redirect(request.path)
