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
    first_name = forms.CharField(max_length=30, required=True)
    surname = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'surname', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the fields are in the correct order
        self.fields['first_name'].label = "First Name"
        self.fields['surname'].label = "Last Name"

class TrainingModuleForm(forms.ModelForm):
    class Meta:
        model = TrainingModule
        fields = ['title', 'description', 'trainer']
        trainer = forms.ModelChoiceField(queryset=Trainer.objects.all(), empty_label="Select a trainer")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure the 'trainer' field uses the custom __str__ method
        self.fields['trainer'].queryset = Trainer.objects.all()  


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