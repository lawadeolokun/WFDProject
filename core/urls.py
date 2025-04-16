# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('modules/', views.module_list, name='module_list'),  # URL to display the training modules
]
