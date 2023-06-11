from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('workouts/', views.workouts, name='workouts'),
    path('workouts/<int:workout_id>/', views.workout, name='workout'),
    path('exercises/', views.ExerciseListView.as_view(), name='exercises'),
    path('exercise/<int:exercise_id>/edit/', views.edit_exercise, name='edit_exercise'),
    path('exercise/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('workouts/add/', views.add_workout, name='add_workout'),
    path('workouts/<int:workout_id>/add-exercise/', views.AddExerciseCreateView.as_view(), name='add_exercise'),
    path('workout/<int:workout_id>/edit/', views.edit_workout, name='edit_workout'),
    path('workout/<int:workout_id>/delete/', views.delete_workout, name='delete_workout'),
    path('exercise_workouts/<str:exercise_name_id>/', views.exercise_workouts, name='exercise_workouts'),
    path('personal-records-by-weight/', views.personal_records_by_weight, name='personal_records_by_weight'),
    path('personal-records-by-reps/', views.personal_records_by_reps, name='personal_records_by_reps'),
    path('workouts-calendar/<int:year>/', views.workout_summary_calendar, name='workout_summary_calendar'),
]
