from django.contrib import admin
from .models import Exercise, Profile, ExerciseName



# Register your models here.
# class ExerciseAdmin(admin.ModelAdmin):
#     list_display = ['exercise_name', 'pic']

class ExerciseNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'pic']

    # list_display = ['exercise_name']

    # list_editable = ['weight', 'set', 'rep']
    # list_filter = ['exercise_name']
    # search_fields = ['exercise_name']
    # fieldsets = (
    #     ('General', {'fields': ('exercise_name', )}),
    #     ('Results', {'fields': ('weight', 'set', 'rep')}),
    # )



# class ExercisesInline(admin.TabularInline):
#     model = models.Exercise
#     extra = 0

# class WorkoutAdmin(admin.ModelAdmin):
#     list_display = ['title', 'athlete', 'date', 'display_exercises']
    # inlines = [ExercisesInline]


# admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(ExerciseName, ExerciseNameAdmin)
# admin.site.register(models.Workout, WorkoutAdmin)
admin.site.register(Profile)




