# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import CustomUserCreationForm, TrainingModuleForm, TrainerForm
from .models import TrainingModule, Enrollment, Student, Trainer, Progress
from django.contrib.auth.models import User
from core.models import User
from django.db.models import Q

def home(request):
    return render(request, 'core/home.html')

def module_list(request):
    query = request.GET.get('q', '')
    modules = TrainingModule.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )

    return render(request, 'core/module_list.html', {'modules': modules, 'query': query})

def enroll_in_module(request, module_id):
    student = Student.objects.get(user=request.user)
    module = TrainingModule.objects.get(id=module_id)

    #Checks to see if student is already enrolled
    if not Enrollment.objects.filter(student=student, module=module).exists():
        Enrollment.objects.create(student=student, module=module)
        return redirect('student_dashboard')
    
    return render(request, 'core/enroll_failed.html', {'message': 'Already enrolled in this module'})

@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "You are not registered as a student.")
        return redirect('home')
    
    enrollments = Enrollment.objects.filter(student=student)
    available_modules = TrainingModule.objects.exclude(id__in=[enrollment.module.id for enrollment in enrollments])

    if not enrollments.exists():
        messages.info(request, "You are not enrolled in any modules.")

    return render(request, 'core/student_dashboard.html', {'enrollments': enrollments, 'available_modules': available_modules,})

@login_required
def trainer_dashboard(request):
    if not request.user.role == 'trainer':
        return redirect('home')
    
    try:
        query = request.GET.get('q', '')  

        trainer = Trainer.objects.get(user=request.user)
        modules = TrainingModule.objects.filter(trainer=trainer).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    except Trainer.DoesNotExist:
        return redirect('home')

    enrollments = Enrollment.objects.filter(module__in=modules)
    module_students = {}
    for module in modules:
        module_students[module] = [
            enrollment.student for enrollment in enrollments if enrollment.module == module
        ]

    return render(request, 'core/trainer_dashboard.html', {
        'modules': modules,
        'module_students': module_students,
        'query': query
    })


@login_required
def track_progress(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)

    if request.user != enrollment.student.user:
        return redirect('home')

    progress, created = Progress.objects.get_or_create(enrollment=enrollment)

    if request.method == 'POST':
        progress_percentage = request.POST.get('progress_percentage')
        completion_status = request.POST.get('completion_status')
        points = request.POST.get('points')

        if progress_percentage is not None:
            progress.progress_percentage = float(progress_percentage)
        if completion_status:
            progress.completion_status = completion_status
        if points is not None:
            progress.points = int(points)

        progress.assign_badge_and_points()  

        progress.save()
        
        messages.success(request, 'Your progress has been updated!')
        return redirect('track_progress', enrollment_id=enrollment.id)

    return render(request, 'core/track_progress.html', {'progress': progress, 'enrollment': enrollment})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  
            
            if user.role == 'student':
                student = Student.objects.create(user=user)
                student.student_id = student.generate_student_id() 
                student.save()

            elif user.role == 'trainer':
                trainer = Trainer.objects.create(user=user)
                trainer.trainer_id = trainer.generate_trainer_id()  
                trainer.save() 
                
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def user_profile(request):
    if request.user.is_staff:
        return redirect('admin_dashboard') 
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('user_list')  
    else:
        form = CustomUserCreationForm()

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
            return redirect('admin_dashboard') 
    else:
        form = UserChangeForm(instance=user)

    return render(request, 'core/update_user.html', {'form': form, 'user': user})

@login_required
def delete_user(request, user_id):
    if not request.user.is_staff: 
        return redirect('home') 
    
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('admin_dashboard')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_list')

@login_required
def user_list(request):
    if not request.user.is_staff: 
        return redirect('home') 
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    )
    return render(request, 'core/user_list.html', {'users': users, 'query': query})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-admin users to the homepage or another page

    # Query using the custom User model (core.User)
    users = User.objects.all()  # Get all users
    modules = TrainingModule.objects.all()  # Get all modules

    context = {
        'users': users,
        'modules': modules,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def create_module(request):
    if not request.user.is_staff and request.user.role != 'trainer':
        return redirect('home')  # Only allow admin to create modules

    if request.method == 'POST':
        form = TrainingModuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Training module created successfully!')
            return redirect('admin_dashboard')  # Redirect to admin dashboard after creating a module
    else:
        form = TrainingModuleForm()

    return render(request, 'core/create_module.html', {'form': form})

def create_trainer(user_instance, trainer_id):
    trainer = Trainer(user=user_instance, trainer_id=trainer_id)
    trainer.save()
    return trainer

@login_required
def assign_student_to_module(request, module_id):
    if not request.user.is_staff and request.user.role != 'trainer':
        return redirect('home') 

    try:
        module = TrainingModule.objects.get(id=module_id)
    except TrainingModule.DoesNotExist:
        messages.error(request, "The module you are trying to assign students to does not exist.")
        return redirect('trainer_dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        
        if not student_id:
            messages.error(request, "No student selected.")
            return redirect('trainer_dashboard')

        try:
            student = Student.objects.get(id=student_id)
            
            if Enrollment.objects.filter(student=student, module=module).exists():
                messages.info(request, f'{student.user.first_name} {student.user.last_name} is already enrolled in this module.')
            else:
                Enrollment.objects.create(student=student, module=module)
                messages.success(request, f'Student {student.user.first_name} {student.user.last_name} successfully enrolled in {module.title}.')

        except Student.DoesNotExist:
            messages.error(request, 'The student you selected does not exist.')
        
        return redirect('assign_student_to_module', module_id=module_id) 

    students = Student.objects.all()
    return render(request, 'core/assign_student_to_module.html', {'module': module, 'students': students})

@login_required
def student_enrollment(request):
    modules = TrainingModule.objects.all()
    
    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        student = Student.objects.get(user=request.user)
        module = TrainingModule.objects.get(id=module_id)

        if not Enrollment.objects.filter(student=student, module=module).exists():
            Enrollment.objects.create(student=student, module=module)
            messages.success(request, f'You have successfully enrolled in {module.title}.')
        else:
            messages.info(request, f'You are already enrolled in {module.title}.')
        
        return redirect('student_dashboard')

    return render(request, 'core/student_enrollment.html', {'modules': modules})

@login_required
def update_module(request, module_id):
    if not request.user.is_staff:
        return redirect('home') 
    
    module = get_object_or_404(TrainingModule, id=module_id)
    
    if request.method == 'POST':
        form = TrainingModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, f'The module "{module.title}" has been updated!')
            return redirect('admin_dashboard') 
    else:
        form = TrainingModuleForm(instance=module)
    
    return render(request, 'core/update_module.html', {'form': form, 'module': module})

@login_required
def delete_module(request, module_id):
    if not request.user.is_staff:
        return redirect('home') 
    
    module = get_object_or_404(TrainingModule, id=module_id)
    
    if request.method == 'POST':
            module.delete()
            messages.success(request, f'The module "{module.title}" has been deleted!')
            return redirect('admin_dashboard') 
    
    return render(request, 'core/delete_module.html', {'module': module})

def student_list(request):
    query = request.GET.get('q', '') 
    filter_module = request.GET.get('module', '') 
    filter_status = request.GET.get('status', '') 
    
    students = Student.objects.all()
    
    if query:
        students = students.filter(
            Q(user__username__icontains=query) | 
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query)
        )
    
    if filter_module:
        students = students.filter(enrollment__module__id=filter_module)
    
    if filter_status:
        students = students.filter(progress__completion_status=filter_status)
    
    return render(request, 'core/student_list.html', {'students': students, 'query': query, 'filter_module': filter_module, 'filter_status': filter_status})