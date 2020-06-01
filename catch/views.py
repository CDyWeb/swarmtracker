import json

import requests
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.views import View
from report.models import SwarmReport
from swarm import RecaptchaView
from swarm.models import SwarmUser
from django.contrib.auth import login as django_login


class SignupForm(ModelForm):
    def _post_clean(self):
        if SwarmUser.objects.filter(email=self.cleaned_data['email']).only('email').count() > 0:
            self.add_error('email', 'This email is already registered')
        return super()._post_clean()

    class Meta:
        fields = '__all__'
        exclude = ['date_joined', 'username', 'password']
        model = SwarmUser


class SignupView(RecaptchaView):
    def get(self, request):
        if request.user and request.user.is_authenticated:
            return redirect('swarms')

        return render(request, 'signup.html', context={
            'recaptcha_key': settings.RECAPTCHA_KEY
        })

    def post(self, request):
        form = SignupForm(data=request.POST.dict())
        if form.is_valid():
            new_user: SwarmUser = form.save(commit=False)

            try:
                map_key = settings.MAPQUESTAPI_KEY
                map_url = f'https://www.mapquestapi.com/geocoding/v1/address?key={map_key}&inFormat=kvp&outFormat=json&location={new_user.zip}%2CCanada&thumbMaps=false'
                print(map_url)
                resp = requests.get(map_url)
                resp.raise_for_status()
                location = json.loads(resp.content).get('results', [])[0].get('locations', [])[0]
                new_user.latitude = location.get('latLng', {}).get('lat')
                new_user.longitude = location.get('latLng', {}).get('lng')
                print(location)
            except:
                pass

            new_user.is_active = True
            new_user.username = new_user.email
            new_user.password = make_password(new_user.zip)
            new_user.save()

            django_login(request, new_user)

            return redirect('signup-done')

        return render(request, 'signup.html', context={
            'recaptcha_key': settings.RECAPTCHA_KEY,
            'signup': form.data,
            'errors': [f'{f}: ' + ', '.join(error) if f != '__all__' else ', '.join(error) for f, error in form.errors.items()]
        })


class SignupDoneView(View):
    def get(self, request):
        return render(request, 'signup-done.html', context={
        })


class SwarmView(View):
    def get(self, request):
        return render(request, 'swarms.html', context={
            'swarms': SwarmReport.objects.filter().only('id', 'created_at', 'latitude', 'longitude', 'location_reverse').order_by('-created_at')
        })
