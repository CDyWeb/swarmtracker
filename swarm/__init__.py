import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views import View


class RecaptchaView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
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

        return super().dispatch(request, *args, **kwargs)
