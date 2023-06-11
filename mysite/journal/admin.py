from django.contrib import admin
from .models import Profile, ExerciseName

# Register your models here.


class ExerciseNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'pic']


admin.site.register(ExerciseName, ExerciseNameAdmin)
admin.site.register(Profile)
