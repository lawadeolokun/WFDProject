from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


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

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trainer_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.trainer_id})"
    
    def save(self, *args, **kwargs):
        """Override save to generate trainer_id if not set"""
        if not self.trainer_id: 
            self.trainer_id = self.generate_trainer_id()
        super().save(*args, **kwargs)

    def generate_trainer_id(self):
        """Generate a unique trainer_id."""
        prefix = "TR-"  
    
        last_trainer = Trainer.objects.all().order_by('-id').first() 

        if last_trainer:
            try:
                last_trainer_number = int(last_trainer.trainer_id.split('-')[1])
                new_trainer_number = last_trainer_number + 1
            except (IndexError, ValueError):
                new_trainer_number = 1
        else:
            new_trainer_number = 1 

        trainer_id = f"{prefix}{str(new_trainer_number).zfill(3)}"
        return trainer_id



# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)

    def generate_student_id(self):
        """Generate a unique student ID."""
        prefix = "ST-"

        last_student = Student.objects.all().order_by('-id').first()

        if last_student:
            try:
                last_student_number = int(last_student.student_id.split('-')[1])
                new_student_number = last_student_number + 1
            except IndexError:
                new_student_number = 1
        else:
            new_student_number = 1

        student_id = f"{prefix}{str(new_student_number).zfill(3)}"
        return student_id


# TrainingModule Model
class TrainingModule(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    module_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.module_id:
            self.module_id = str(uuid.uuid4()).split('-')[0].upper()  
        super().save(*args, **kwargs)

# Enrollment Model
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.first_name} enrolled in {self.module.title}"

# Progress Model
class Progress(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0.0)
    completion_status = models.CharField(max_length=20, default='in-progress')
    points = models.IntegerField(default=0)  # Points for gamification
    badge_earned = models.CharField(max_length=50, blank=True)  # Badge earned for completing challenges

    def __str__(self):
        return f"Progress for {self.enrollment.student.user.first_name} in {self.enrollment.module.title}"
    
    def assign_badge_and_points(self):
        if self.progress_percentage >= 100:
            self.badge_earned = "Platinum"
            self.points = 100
            self.completion_status = "Completed"
        elif self.progress_percentage >= 75:
            self.badge_earned = "Gold"
            self.points = 75
        elif self.progress_percentage >= 50:
            self.badge_earned = "Silver"
            self.points = 50
        elif self.progress_percentage >= 25:
            self.badge_earned = "Bronze"
            self.points = 25
        else:
            self.progress_percentage = 0
            self.badge_earned = "No Badge"
            self.completion_status = "in-progress"

    def save(self, *args, **kwargs):
        self.assign_badge_and_points()
        super().save(*args, **kwargs)
