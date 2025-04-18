# core/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('modules/', views.module_list, name='module_list'),  # URL to display the training modules
    path('enroll/<int:module_id>/', views.enroll_in_module, name='enroll_in_module'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('trainer_dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('progress/<int:enrollment_id>/', views.track_progress, name='track_progress'),
    path('register/', views.register, name='register'),
    path('login/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', views.user_profile, name='profile'), 
    path('create/', views.create_user, name='create_user'), 
    path('update/<int:user_id>/', views.update_user, name='update_user'),  # Update user page
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),  # Delete user page
    path('users/', views.user_list, name='user_list'),  # List all users page
    path('profile/', views.user_profile, name='user_profile'),  
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),  
    path('trainer_dashboard/', views.trainer_dashboard, name='trainer_dashboard'), 

]
