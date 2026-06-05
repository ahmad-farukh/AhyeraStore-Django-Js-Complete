# core/urls.py
from django.urls import path
from . import views

app_name = 'core'  # ADD THIS LINE

urlpatterns = [
    path('', views.home_view, name='home'),
    # Add other core URLs
]