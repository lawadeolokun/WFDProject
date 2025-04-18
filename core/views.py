# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import CustomUserCreationForm
from .models import TrainingModule, Enrollment, Student, Trainer, Progress
from django.contrib.auth.models import User

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

    if not enrollments.exists():
        messages.info(request, "You are not enrolled in any modules.")

    return render(request, 'core/student_dashboard.html', {'enrollments': enrollments})

@login_required
def trainer_dashboard(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
        modules = TrainingModule.objects.filter(trainer=trainer)
    except Trainer.DoesNotExist:
        return redirect('home')
    
    return render(request, 'core/trainer_dashboard.html', {'modules': modules})

def track_progress(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)
    progress = Progress.objects.filter(enrollment=enrollment).first()
    return render(request, 'core/track_progress.html', {'progress': progress, 'enrollment': enrollment})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  
            if user.role == 'student':
                Student.objects.create(user=user)
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_profile(request):
    if request.user.is_staff:
        return redirect('/admin/') 
    elif request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'trainer':
        return redirect('trainer_dashboard')
    else:
        return redirect('home')  
    
@login_required
def create_user(request):
    if not request.user.is_staff:  
        return redirect('home')  

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('user_list')  
    else:
        form = UserCreationForm()

    return render(request, 'core/create_user.html', {'form': form})

@login_required
def update_user(request, user_id):
    if not request.user.is_staff: 
        return redirect('home')  

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_list')

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list') 
    else:
        form = UserChangeForm(instance=user)

    return render(request, 'core/update_user.html', {'form': form, 'user': user})

@login_required
def delete_user(request, user_id):
    if not request.user.is_staff: 
        return redirect('home')  

@login_required
def user_list(request):
    if not request.user.is_staff: 
        return redirect('home') 
    users = User.objects.all()
    return render(request, 'core/user_list.html', {'users': users})

@login_required
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')