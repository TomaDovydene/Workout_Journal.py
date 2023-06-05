from django.contrib import admin
from . import models



# Register your models here.
class ExerciseAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        return ['exercise_name', 'pic']



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


admin.site.register(models.Exercise, ExerciseAdmin)
# admin.site.register(models.Workout, WorkoutAdmin)
admin.site.register(models.Profile)




