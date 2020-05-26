from django.urls import path

from . import views

urlpatterns = [
    path('catch-a-swarm', views.SignupView.as_view(), name='signup'),
    path('swarms', views.SwarmView.as_view(), name='swarms'),
]
