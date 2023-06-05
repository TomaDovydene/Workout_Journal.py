import itertools

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy

from .models import Exercise, Workout, ExerciseName
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, WorkoutForm, ExerciseForm
from django.db.models import Count, Sum, Q, Max


# Create your views here.


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, f'User name {username} already exists!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'User email {email} already exists!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'Username {username} registered!')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
    return render(request, 'registration/register.html')


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.info(request, f"Profilis atnaujintas")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'profile.html', context)


def index(request):
    num_exercises = Exercise.objects.all().count()

    num_workouts = Workout.objects.count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_exercises': num_exercises,
        'num_workouts': num_workouts,
        'num_visits': num_visits,
    }
    return render(request, 'index.html', context=context)


def workouts(request):
    query = request.GET.get('query')
    sort_by = request.GET.get('sort')
    workouts = Workout.objects.all()

    if query:
        workouts = workouts.filter(Q(title__icontains=query) | Q(date__icontains=query))


    if sort_by == 'title':
        workouts = workouts.order_by('title')
    elif sort_by == 'date':
        workouts = workouts.order_by('date')


    context = {
        'workouts': workouts,
        'query': query if query else '',
    }
    return render(request, 'workouts.html', context=context)


def workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    context = {
        'workout': workout,
    }
    return render(request, 'workout.html', context=context)


def add_workout(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save()
            return redirect('workout', workout_id=workout.id)
    else:
        form = WorkoutForm()

    context = {
        'form': form,
    }
    return render(request, 'add_workout.html', context=context)


def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)

    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            return redirect('workouts')
    else:
        form = WorkoutForm(instance=workout)

    context = {
        'form': form,
        'workout': workout,
    }
    return render(request, 'edit_workout.html', context=context)

def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)

    if request.method == 'POST':
        workout.delete()
        return redirect('workouts')

    context = {
        'workout': workout,
    }
    return render(request, 'delete_workout.html', context=context)




class ExerciseListView(LoginRequiredMixin, generic.ListView):
    model = Exercise
    context_object_name = 'exercises'
    template_name = 'exercises.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        exercises = context['exercises']

        # Exclude exercises without exercise names
        exercises_with_names = [exercise for exercise in exercises if exercise.exercise_name]

        # Group exercises by name
        grouped_exercises = []
        exercises_with_names = sorted(exercises_with_names,
                                      key=lambda exercise: exercise.exercise_name.name)  # Sort exercises by name
        for name, group in itertools.groupby(exercises_with_names, key=lambda exercise: exercise.exercise_name.name):
            grouped_exercises.append(list(group))

        context['exercises'] = grouped_exercises

        return context


def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)

    if request.method == 'POST':
        exercise.weight = request.POST['weight']
        exercise.set = request.POST['set']
        exercise.rep = request.POST['rep']
        exercise.save()
        return redirect('workout', workout_id=exercise.workout.id)
    return render(request, 'edit_exercise.html', {'exercise': exercise})


def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)

    if request.method == 'POST':
        exercise.delete()
        return redirect('workout', workout_id=exercise.workout.id)
    return render(request, 'delete_exercise.html', {'exercise': exercise})



class AddExerciseCreateView(LoginRequiredMixin, generic.CreateView):
    model = Exercise
    template_name = 'add_exercise.html'
    form_class = ExerciseForm

    def form_valid(self, form):
        form.instance.athlete = self.request.user
        exercise_name_id = form.cleaned_data['exercise_name']
        custom_exercise_name = form.cleaned_data['custom_exercise_name']
        workout_id = self.kwargs['workout_id']
        workout = get_object_or_404(Workout, pk=workout_id)

        if exercise_name_id:
            form.instance.exercise_name_id = exercise_name_id
        elif custom_exercise_name:
            custom_exercise, _ = ExerciseName.objects.get_or_create(name=custom_exercise_name)
            form.instance.exercise_name = custom_exercise
            form.instance.custom_exercises.add(self.request.user)

        form.instance.workout = workout
        return super().form_valid(form)

    def get_success_url(self):
        workout_id = self.kwargs['workout_id']
        return reverse_lazy('workout', kwargs={'workout_id': workout_id})


class CustomExerciseCreateView(LoginRequiredMixin, generic.CreateView):
    model = Exercise
    fields = ['exercise_name', 'weight', 'set', 'rep']
    template_name = 'add_custom_exercise.html'

    def get_success_url(self):
        workout_id = self.kwargs['workout_id']
        return reverse_lazy('workout', kwargs={'workout_id': workout_id})




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context



# def exercise_workouts(request, exercise_name_id):
#     exercise_name = ExerciseName.objects.get(id=exercise_name_id)
#
#     query = request.GET.get('query')
#
#     # Get the sorting parameter from the request
#     sort_by = request.GET.get('sort')
#
#     # Filter the workouts based on the exercise_name
#     workouts = Workout.objects.filter(exercises__exercise_name=exercise_name)
#
#     if query:
#         workouts = workouts.filter(
#             Q(title__icontains=query) |
#             Q(date__icontains=query)
#         )
#
#     # Create a dictionary to store workout information
#     workout_info = []
#
#     # Iterate over the filtered workouts
#     for workout in workouts:
#         # Get the exercises for the current workout and exercise name
#         exercises = workout.exercises.filter(exercise_name=exercise_name)
#
#         # Calculate the total weight for the exercise in the workout
#         total_weight = exercises.aggregate(Sum('weight'))['weight__sum']
#
#         # Store the workout information in the list
#         workout_info.append({
#             'workout': workout,
#             'total_weight': total_weight,
#             'exercises': exercises
#         })
#
#     # Sort the workouts based on the sorting parameter
#     if sort_by == 'weight':
#         workout_info.sort(key=lambda x: x['total_weight'], reverse=True)
#
#     context = {
#         'workout_info': workout_info,
#         'exercise_name': exercise_name,
#         'query': query if query else '',
#     }
#
#     return render(request, 'exercise_workouts.html', context=context)


def exercise_workouts(request, exercise_name_id):
    # Clean up exercise_name by stripping whitespace

    exercise_name = ExerciseName.objects.get(id=exercise_name_id)
    query = request.GET.get('search')

    # Get the sorting parameter from the request
    sort_by = request.GET.get('sort')

    # Filter the workouts based on the exercise_name
    workouts = Workout.objects.filter(exercises__exercise_name__exact=exercise_name).distinct()

    if query:
        workouts = workouts.filter(
            Q(title__icontains=query) |
            Q(date__icontains=query)
        )

    # Create a dictionary to store workout information
    workout_info = {}

    # Iterate over the filtered workouts
    for workout in workouts:
        # Get the exercises for the current workout and exercise name
        exercises = workout.exercises.filter(exercise_name__exact=exercise_name)

        # Calculate the total weight for the exercise in the workout
        total_weight = exercises.aggregate(Sum('weight'))['weight__sum']

        # Store the workout information in the dictionary
        workout_info[workout] = {
            'total_weight': total_weight,
            'exercises': exercises
        }

    # Sort the workouts based on the sorting parameter
    if sort_by == 'weight':
        workout_info = sorted(workout_info.items(), key=lambda x: x[1]['total_weight'], reverse=True)

    context = {
        'workout_info': workout_info,
        'exercise_name': exercise_name,
        'query': query if query else '',
    }

    return render(request, 'exercise_workouts.html', context=context)


def personal_records_by_weight(request):
    query = request.GET.get('query')
    exercises = Exercise.objects.all()

    if query:
        exercises = exercises.filter(
            Q(exercise_name__name__icontains=query)
        )

    top_weight_workouts = {}

    for exercise in exercises:
        if exercise.exercise_name:  # Check if exercise has a non-null exercise_name
            workouts = Workout.objects.filter(exercises__exercise_name__name__icontains=exercise.exercise_name.name).annotate(
                max_weight=Max('exercises__weight')).order_by('-max_weight')[:3]

            top_weight_workouts[exercise.exercise_name.name] = []

            for workout in workouts:
                exercise_instance = workout.exercises.filter(exercise_name__name__icontains=exercise.exercise_name.name).order_by('-weight').first()

                if exercise_instance:
                    top_weight_workouts[exercise.exercise_name.name].append((workout, exercise_instance))

    context = {
        'top_weight_workouts': top_weight_workouts,
        'query': query if query else '',
        'all_exercises': Exercise.objects.values_list('exercise_name__name', flat=True).distinct()
    }

    return render(request, 'personal_records_by_weight.html', context=context)



def personal_records_by_reps(request):
    query = request.GET.get('query')
    exercises = Exercise.objects.all()

    if query:
        exercises = exercises.filter(
            Q(exercise_name__name__icontains=query)
        )

    top_rep_workouts = {}

    for exercise in exercises:
        if exercise.exercise_name:  # Check if exercise has a non-null exercise_name
            workouts = Workout.objects.filter(exercises__exercise_name__name__icontains=exercise.exercise_name.name).annotate(
                max_rep=Max('exercises__rep')).order_by('-max_rep')[:3]

            top_rep_workouts[exercise.exercise_name.name] = []

            for workout in workouts:
                exercise_instance = workout.exercises.filter(exercise_name__name__icontains=exercise.exercise_name.name).order_by('-rep').first()

                if exercise_instance:
                    top_rep_workouts[exercise.exercise_name.name].append((workout, exercise_instance))

    context = {
        'top_rep_workouts': top_rep_workouts,
        'query': query if query else '',
    }

    return render(request, 'personal_records_by_reps.html', context=context)

