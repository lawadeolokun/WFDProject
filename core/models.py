from django.db import models
from django.contrib.auth.models import AbstractUser

# User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',  # Changed related_name
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions',  # Changed related_name
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )
# Admin Model
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_id = models.CharField(max_length=20, unique=True)

# Trainer Model
class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trainer_id = models.CharField(max_length=20, unique=True)

# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)

# TrainingModule Model
class TrainingModule(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    module_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Enrollment Model
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

# Progress Model
class Progress(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    progress_percentage = models.FloatField()
    completion_status = models.CharField(max_length=20)
    points = models.IntegerField(default=0)  # Points for gamification
    badge_earned = models.CharField(max_length=50, blank=True)  # Badge earned for completing challenges
