from django.contrib import admin
from .models import User, Admin, Trainer, Student, TrainingModule, Enrollment, Progress

class TrainerAdmin(admin.ModelAdmin):
    list_display = ['trainer_id', 'user']  # Display trainer and user fields
    search_fields = ['trainer_id', 'user__username']  # Allow search by trainer_id or user username
    list_filter = ['user']  # Filter by user (if needed)
    
    # Ensure User field is displayed properly and allows linking
    def save_model(self, request, obj, form, change):
        # Ensure the user is set before saving
        if not obj.user:
            obj.user = User.objects.get(username=request.user.username)  # Set the logged-in user as a trainer
        super().save_model(request, obj, form, change)

class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer']
    search_fields = ['title', 'trainer__user__username']



# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Trainer, TrainerAdmin)
admin.site.register(Student)
admin.site.register(TrainingModule, TrainingModuleAdmin)
admin.site.register(Enrollment)
admin.site.register(Progress)


