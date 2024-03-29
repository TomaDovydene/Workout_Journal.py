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
    notes = forms.CharField(max_length=200, required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, **kwargs):
        super(WorkoutForm, self).__init__(*args, **kwargs)
        self.fields['date'].required = True

    class Meta:
        model = Workout
        fields = ['title', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD', 'style': 'color: #020202'}),
        }


class ExerciseForm(forms.ModelForm):
    custom_exercise_name = forms.CharField(max_length=100, required=False)
    notes = forms.CharField(max_length=200, required=False, widget=forms.Textarea(attrs={'rows': 3}))
    weight = forms.FloatField(required=True)
    rep = forms.IntegerField(required=True)
    set = forms.IntegerField(required=True)

    class Meta:
        model = Exercise
        fields = ['exercise_name', 'custom_exercise_name', 'weight', 'set', 'rep', 'notes']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['exercise_name'].queryset = ExerciseName.objects.filter(
            Q(created_by__isnull=True) | Q(created_by=self.user) | Q(created_by_id=1)
        ).order_by('name')

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
