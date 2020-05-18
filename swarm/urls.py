from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = []

urlpatterns += [
    url(r'^swarm-admin/', admin.site.urls),
    url(r'', include('django.conf.urls.i18n')),
    url(r'', include('home.urls')),
    url(r'', include('report.urls')),
    url(r'', include('catch.urls')),
    url(r'', include('auth0_client.urls')),
]

# if settings.DEBUG and os.getenv('GAE_INSTANCE'):
#     urlpatterns += static('/static/', document_root=settings.STATIC_ROOT)
