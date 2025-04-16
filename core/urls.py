# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('modules/', views.module_list, name='module_list'),  # URL to display the training modules
    path('enroll/<int:module_id>/', views.enroll_in_module, name='enroll_in_module'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('trainer_dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('progress/<int:enrollment_id>/', views.track_progress, name='track_progress'),
]
