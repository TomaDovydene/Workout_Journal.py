from .models import Profile, Workout, Exercise, ExerciseName
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q


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
        fields = ['title', 'date']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class ExerciseForm(forms.ModelForm):
    custom_exercise_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Exercise
        fields = ['exercise_name', 'custom_exercise_name', 'weight', 'set', 'rep']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Retrieve the 'user' argument from kwargs
        super().__init__(*args, **kwargs)

        # Filter exercise name choices based on custom exercises added by the user and exercise names created by the superuser
        self.fields['exercise_name'].queryset = ExerciseName.objects.filter(
            Q(created_by__isnull=True) | Q(created_by=self.user) | Q(created_by_id=1)
        )

    def clean(self):
        cleaned_data = super().clean()
        exercise_name = cleaned_data.get('exercise_name')
        custom_exercise_name = cleaned_data.get('custom_exercise_name')

        if not exercise_name and not custom_exercise_name:
            raise forms.ValidationError('Please select an exercise name or enter a custom exercise name.')

        return cleaned_data

    def save(self, commit=True):
        exercise = super().save(commit=False)
        custom_exercise_name = self.cleaned_data.get('custom_exercise_name')

        if custom_exercise_name:
            exercise_name, _ = ExerciseName.objects.get_or_create(name=custom_exercise_name, created_by=self.user)
            exercise.exercise_name = exercise_name

        if commit:
            exercise.save()

        return exercise




















