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
        
        # Create corresponding Student object (if Student is a model extending User)
        self.student = Student.objects.create(user=self.student_user)
        
        # Create corresponding Trainer object
        self.trainer = Trainer.objects.create(user=self.trainer_user)

        # Create Training Module with a Trainer
        self.module = TrainingModule.objects.create(title="Python Basics", description="Learn Python basics", trainer=self.trainer)
        
        # Enroll student in module (assign a Student instance)
        self.enrollment = Enrollment.objects.create(student=self.student, module=self.module)

    def test_admin_access(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertTrue(response.status_code == 200)

    def test_trainer_access(self):
        self.client.login(username="trainer1", password="password")
        response = self.client.get(reverse('trainer_dashboard'))
        self.assertTrue(response.status_code == 200)

    def test_student_access(self):
        self.client.login(username="student1", password="password")
        response = self.client.get(reverse('student_dashboard'))
        self.assertTrue(response.status_code == 200)

    def test_student_enroll_module(self):
        self.client.login(username="student1", password="password")
        # Try to enroll in the module (shouldn't fail as student is already enrolled)
        response = self.client.post(reverse('enroll_in_module', args=[self.module.id]))
        self.assertTrue(response.status_code == 200)  # Enrollment page rendered correctly

    def test_admin_update_module(self):
        self.client.login(username="admin", password="password")
        # Update the module title
        response = self.client.post(reverse('update_module', args=[self.module.id]), {'title': 'Updated Python Basics'})
        self.assertTrue(response.status_code == 200)  # Check if the page renders without redirects

    def test_trainer_enroll_student(self):
        self.client.login(username="trainer1", password="password")
        # Trainer tries to enroll a student (simulated by post request)
        response = self.client.post(reverse('assign_student_to_module', args=[self.module.id]), {'student_id': self.student_user.id})
        self.assertTrue(response.status_code == 200)  # Check if the form is submitted correctly

    def test_user_login(self):
        response = self.client.post(reverse('login'), {'username': 'student1', 'password': 'password'})
        self.assertTrue(response.status_code == 200)  # Check if login page renders correctly

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {'username': 'user2', 'password1': 'password', 'password2': 'password', 'email': 'user2@user.com'})
        self.assertTrue(response.status_code == 200)  # Check if registration page renders correctly
