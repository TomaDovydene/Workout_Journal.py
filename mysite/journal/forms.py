from .models import Profile, Workout, Exercise
from django import forms
from django.contrib.auth.models import User


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['athlete', 'title', 'date']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class ExerciseForm(forms.ModelForm):
    custom_exercise_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Exercise
        fields = ['exercise_name', 'custom_exercise_name', 'weight', 'set', 'rep']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        predefined_exercises = Exercise.EXERCISES_LIST
        user_custom_exercises = Exercise.objects.filter(athlete=user).values_list('custom_exercises__exercise_name', flat=True).distinct()
        exercise_choices = list(predefined_exercises) + list(user_custom_exercises)
        self.fields['exercise_name'].choices = exercise_choices



