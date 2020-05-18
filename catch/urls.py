from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^catch$', views.CatchView.as_view(), name='catch'),
]
