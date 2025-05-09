from django.test import TestCase
from django.urls import reverse
from core.models import Trainer, Student, TrainingModule, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTestCase(TestCase):

    def setUp(self):
        # Create Users
        self.admin_user = User.objects.create_user(username="admin", email="admin@admin.com", password="password", is_staff=True)
        self.student_user = User.objects.create_user(username="student1", email="student1@user.com", password="password")
        self.trainer_user = User.objects.create_user(username="trainer1", email="trainer1@user.com", password="password")
        
        # Create Student object (if Student is a model extending User)
        self.student = Student.objects.create(user=self.student_user)
        
        # Create  Trainer object
        self.trainer = Trainer.objects.create(user=self.trainer_user)

        # Create Training Module with a Trainer
        self.module = TrainingModule.objects.create(title="Leisure Fun", description="random description", trainer=self.trainer)
        
        # Enroll student in module
        self.enrollment = Enrollment.objects.create(student=self.student, module=self.module)

    def test_admin_access(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertTrue(response.status_code == 200)


    def test_student_access(self):
        self.client.login(username="student1", password="password")
        response = self.client.get(reverse('student_dashboard'))
        self.assertTrue(response.status_code == 200)

    def test_student_enroll_module(self):
        self.client.login(username="student1", password="password")
        # Try to enroll in the module
        response = self.client.post(reverse('enroll_in_module', args=[self.module.id]))
        self.assertRedirects(response, reverse('student_dashboard'))


    def test_admin_update_module(self):
        self.client.login(username="admin", password="password")
        # Update the module title
        response = self.client.post(reverse('update_module', args=[self.module.id]), {'title': 'Updated Python Basics'})
        self.assertTrue(response.status_code == 200)


    def test_user_registration(self):
        response = self.client.post(reverse('register'), {'username': 'user2', 'password1': 'password', 'password2': 'password', 'email': 'user2@user.com'})
        self.assertTrue(response.status_code == 200)  
