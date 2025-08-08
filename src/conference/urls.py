from django.urls import path

app_name = 'conference'
from . import views

urlpatterns = [
    path('request/conference/', views.RequestToConference.as_view(), name='request_access'),
]