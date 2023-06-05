from .models import Profile, Workout, Exercise, ExerciseName
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
        fields = ['custom_exercise_name', 'weight', 'set', 'rep']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exercise_choices = [(name.id, name.name) for name in ExerciseName.objects.all()]
        self.fields['exercise_name'] = forms.ChoiceField(choices=exercise_choices, required=False)



