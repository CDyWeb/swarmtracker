from django.urls import path

from . import views

urlpatterns = [
    path('swarm/<str:uuid>', views.ReportDetailsView.as_view(), name='swarm-details'),
    path('report-done', views.ReportDoneView.as_view(), name='report-done'),
    path('report-a-swarm', views.ReportView.as_view(), name='report-swarm'),
]
