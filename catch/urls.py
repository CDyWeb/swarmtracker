from django.urls import path

from . import views

urlpatterns = [
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('catch-a-swarm', views.SignupView.as_view(), name='signup'),
    path('signup-done', views.SignupDoneView.as_view(), name='signup-done'),
    path('swarms', views.SwarmView.as_view(), name='swarms'),
]
