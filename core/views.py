# core/views.py
from django.shortcuts import render
from .models import TrainingModule

def module_list(request):
    modules = TrainingModule.objects.all()  # Get all training modules
    return render(request, 'core/module_list.html', {'modules': modules})
