from django.contrib import admin
from .models import User, Admin, Trainer, Student, TrainingModule, Enrollment, Progress

# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Trainer)
admin.site.register(Student)
admin.site.register(TrainingModule)
admin.site.register(Enrollment)
admin.site.register(Progress)


