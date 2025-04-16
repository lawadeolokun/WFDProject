# core/views.py
from django.shortcuts import render, redirect
from .models import TrainingModule, Enrollment, Student, Trainer, Progress

def home(request):
    return render(request, 'core/home.html')

def module_list(request):
    modules = TrainingModule.objects.all()  # Get all training modules
    return render(request, 'core/module_list.html', {'modules': modules})

def enroll_in_module(request, module_id):
    student = Student.objects.get(user=request.user)
    module = TrainingModule.objects.get(id=module_id)

    #Checks to see if student is already enrolled
    if not Enrollment.objects.filter(student=student, module=module).exists():
        Enrollment.objects.create(student=student, module=module)
        return redirect('student_dashboard')
    
    return render(request, 'core/enroll_failed.html', {'message': 'Already enrolled in this module'})

def student_dashboard(request):
    student = Student.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(student=student)
    return render(request, 'core/student_dashboard.html', {'enrollments': enrollments})

def trainer_dashboard(request):
    trainer = Trainer.objects.get(user=request.user)
    modules = TrainingModule.objects.filter(trainer=trainer)
    return render(request, 'core/trainer_dashboard.html', {'modules': modules})

def track_progress(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)
    progress = Progress.objects.filter(enrollment=enrollment).first()
    return render(request, 'core/track_progress.html', {'progress': progress, 'enrollment': enrollment})