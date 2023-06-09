from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse
from PIL import Image

# Create your models here.
class ExerciseName(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pic = models.ImageField(verbose_name='Pic', upload_to='pics', null=True, blank=True)
    created_by = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True, related_name='created_exercise_names')

    def __str__(self):
        return self.name


class Exercise(models.Model):
    athlete = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    workout = models.ForeignKey(to='Workout', verbose_name='Workout', on_delete=models.SET_NULL, null=True, related_name='exercises')
    set = models.IntegerField(verbose_name='Set', null=True, blank=True)
    rep = models.IntegerField(verbose_name='Rep', null=True, blank=True)
    weight = models.FloatField(verbose_name='Weight', null=True, blank=True)
    exercise_name = models.ForeignKey(to='ExerciseName', on_delete=models.SET_NULL, null=True, blank=True)
    custom_exercises = models.ManyToManyField(to=User, related_name='custom_exercises', blank=True)
    notes = models.TextField(verbose_name='Notes', null=True, blank=True)

    def __str__(self):
        return self.exercise_name.name if self.exercise_name else ''


    # def total(self):
    #     total = 0
    #     exercises = self.exercises.all()
    #     for exercise in exercises:
    #         total += exercise.sum()
    #     return total

    def get_absolute_url(self):
        return reverse('exercise_workouts', args=[str(self.id)])

    def get_name(self):
        return self.exercise_name


    def sum(self):
        return self.weight * self.set * self.rep



class Workout(models.Model):
    athlete = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(verbose_name="Title", max_length=100)
    date = models.DateField(verbose_name="Date", null=True, blank=True)
    notes = models.TextField(verbose_name="Notes", null=True, blank=True)

    def get_absolute_url(self):
        return reverse('workout', args=[str(self.id)])


    def __str__(self):
        formatted_date = datetime.strftime(self.date, '%Y-%m-%d')
        return f'{self.title} {formatted_date}'

    class Meta:
        ordering = ['-date']

    def display_exercises(self):
        return ', '.join(exercise.exercise_name.name for exercise in self.exercises.all())

    display_exercises.short_description = 'Exercises'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(default="profile_pics/Default.png", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.photo.path)
        if img.height > 100 or img.width > 100:
            output_size = (100, 100)
            img.thumbnail(output_size)
            img.save(self.photo.path)

