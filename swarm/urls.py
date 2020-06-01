from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from django.urls import path


def logout(request):
    django_logout(request)
    return redirect('home')


urlpatterns = [
    url(r'^swarm-admin/', admin.site.urls),
    url(r'', include('django.conf.urls.i18n')),
    url(r'', include('home.urls')),
    url(r'', include('report.urls')),
    url(r'', include('catch.urls')),
    path('logout', logout),
]

# if settings.DEBUG and os.getenv('GAE_INSTANCE'):
#     urlpatterns += static('/static/', document_root=settings.STATIC_ROOT)
