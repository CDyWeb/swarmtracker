from django.urls import path

from . import views

urlpatterns = [
    path('catch-a-swarm', views.CatchView.as_view(), name='catch'),
]
