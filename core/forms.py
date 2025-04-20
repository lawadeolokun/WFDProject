from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, TrainingModule, Trainer

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('admin', 'Admin'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role')  

class TrainingModuleForm(forms.ModelForm):
    class Meta:
        model = TrainingModule
        fields = ['title', 'description', 'trainer']
        trainer = forms.ModelChoiceField(queryset=Trainer.objects.all(), empty_label="Select a trainer")


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['trainer_id', 'user']

    def save(self, commit=True):
        # Ensure User is saved first before Trainer
        user = self.cleaned_data['user']
        user.save()  # Ensure user is saved
        trainer = super().save(commit=False)
        trainer.user = user  # Ensure Trainer is linked to the User
        if commit:
            trainer.save()
        return trainer