from django.conf import settings
from django.contrib.auth import authenticate, login
from django.forms import Form, CharField
from django.shortcuts import render
from django.views import View


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class LoginForm(Form):
    email = CharField()
    password = CharField()


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', context={
            'recaptcha_key': settings.RECAPTCHA_KEY
        })

    def post(self, request):
        form = LoginForm(request.POST.dict())
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password'),
            )
            if user:
                login(request, user)
            else:
                form.add_error(None, 'Login failed')
        return render(request, 'login.html', context={
            'recaptcha_key': settings.RECAPTCHA_KEY,
            'errors': [f'{f}: ' + ', '.join(error) if f != '__all__' else ', '.join(error) for f, error in form.errors.items()]
        })
