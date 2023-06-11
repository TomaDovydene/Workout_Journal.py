import itertools
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import Exercise, Workout, ExerciseName
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, WorkoutForm, ExerciseForm
from django.db.models import Sum, Q
from datetime import date, datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator

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
    return render(request, 'index.html')


@login_required
def workouts(request):
    query = request.GET.get('query')
    sort_by = request.GET.get('sort')
    workouts = Workout.objects.filter(athlete=request.user)

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


@login_required
def workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, athlete=request.user)
    context = {
        'workout': workout,
    }
    return render(request, 'workout.html', context=context)


@login_required
def add_workout(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.athlete = request.user
            workout.save()
            return redirect('workout', workout_id=workout.id)
    else:
        form = WorkoutForm()

    context = {
        'form': form,
    }
    return render(request, 'add_workout.html', context=context)


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, athlete=request.user)

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


@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, athlete=request.user)

    if request.method == 'POST':
        workout.delete()
        return redirect('workouts')

    context = {
        'workout': workout,
    }
    return render(request, 'delete_workout.html', context=context)


@method_decorator(login_required, name='dispatch')
class ExerciseListView(LoginRequiredMixin, generic.ListView):
    model = Exercise
    context_object_name = 'exercises'
    template_name = 'exercises.html'
    paginate_by = 30

    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = Exercise.objects.filter(athlete=self.request.user)

        if query:
            # Filter exercises by exercise name containing the search query
            queryset = queryset.filter(exercise_name__name__icontains=query)

        queryset = queryset.order_by('pk')

        return queryset

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


@login_required
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, athlete=request.user)

    if request.method == 'POST':
        exercise.weight = request.POST['weight']
        exercise.set = request.POST['set']
        exercise.rep = request.POST['rep']
        exercise.notes = request.POST['notes']

        if exercise.exercise_name and exercise.exercise_name.created_by_id != 1:
            # Allow editing of exercise name for exercise names not created by user ID 1
            custom_exercise_name = request.POST.get('custom_exercise_name')
            if custom_exercise_name:
                exercise_name, created = ExerciseName.objects.get_or_create(name=custom_exercise_name)
                exercise.exercise_name = exercise_name

        exercise.save()
        return redirect('workout', workout_id=exercise.workout.id)

    return render(request, 'edit_exercise.html', {'exercise': exercise})


@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, athlete=request.user)

    if request.method == 'POST':
        exercise.delete()
        return redirect('workout', workout_id=exercise.workout.id)
    return render(request, 'delete_exercise.html', {'exercise': exercise})


@method_decorator(login_required, name='dispatch')
class AddExerciseCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Exercise
    template_name = 'add_exercise.html'
    form_class = ExerciseForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.user = self.request.user
        return form

    def test_func(self):
        workout = get_object_or_404(Workout, pk=self.kwargs['workout_id'])
        return workout.athlete == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

    def form_valid(self, form):
        form.instance.athlete = self.request.user
        exercise_name_id = form.cleaned_data['exercise_name']
        custom_exercise_name = form.cleaned_data['custom_exercise_name']
        workout_id = self.kwargs['workout_id']
        workout = get_object_or_404(Workout, pk=workout_id)

        if exercise_name_id:
            form.instance.exercise_name = exercise_name_id
        elif custom_exercise_name:
            exercise = form.save(commit=False)
            exercise.save()
            custom_exercise, _ = ExerciseName.objects.get_or_create(name=custom_exercise_name)
            exercise.exercise_name = custom_exercise
            exercise.save()
            exercise.custom_exercises.add(self.request.user)

        form.instance.workout = workout
        return super().form_valid(form)

    def get_success_url(self):
        workout_id = self.kwargs['workout_id']
        return reverse_lazy('workout', kwargs={'workout_id': workout_id})


@login_required
def exercise_workouts(request, exercise_name_id):
    # Clean up exercise_name by stripping whitespace

    exercise_name = ExerciseName.objects.get(id=exercise_name_id)
    query = request.GET.get('search')

    # Get the sorting parameter from the request
    sort_by = request.GET.get('sort')

    # Filter the workouts based on the exercise_name
    workouts = Workout.objects.filter(
        athlete=request.user,
        exercises__exercise_name__exact=exercise_name).distinct()

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


@login_required
def personal_records_by_weight(request):
    query = request.GET.get('query')
    exercises = Exercise.objects.filter(athlete=request.user)

    if query:
        exercises = exercises.filter(
            Q(exercise_name__name__icontains=query)
        )

    exercises = exercises.order_by('exercise_name__name')

    paginator = Paginator(exercises, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    top_weight_workouts = {}

    for exercise in page_obj:
        if exercise.exercise_name:
            exercise_instances = Exercise.objects.filter(
                athlete=request.user,
                exercise_name__name__iexact=exercise.exercise_name.name
            ).order_by('-weight')

            if exercise_instances:
                workout_ids = exercise_instances.values_list('workout_id', flat=True).distinct()[:1]
                workouts = Workout.objects.filter(id__in=workout_ids)

                top_weight_workouts[exercise.exercise_name.name] = []

                for workout in workouts:
                    exercises_in_workout = exercise_instances.filter(workout_id=workout.id)
                    top_weight_workouts[exercise.exercise_name.name].extend(
                        [(workout, exercise) for exercise in exercises_in_workout[:1]])

    context = {
        'top_weight_workouts': top_weight_workouts,
        'query': query if query else '',
        'page_obj': page_obj,
    }

    return render(request, 'personal_records_by_weight.html', context=context)


@login_required
def personal_records_by_reps(request):
    query = request.GET.get('query')
    exercises = Exercise.objects.filter(athlete=request.user)

    if query:
        exercises = exercises.filter(
            Q(exercise_name__name__icontains=query)
        )

    exercises = exercises.order_by('exercise_name__name')

    paginator = Paginator(exercises, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    top_rep_workouts = {}

    for exercise in page_obj:
        if exercise.exercise_name:
            exercise_instances = Exercise.objects.filter(
                athlete=request.user,
                exercise_name__name__iexact=exercise.exercise_name.name
            ).order_by('-rep')

            if exercise_instances:
                workout_ids = exercise_instances.values_list('workout_id', flat=True).distinct()[:1]
                workouts = Workout.objects.filter(id__in=workout_ids)

                top_rep_workouts[exercise.exercise_name.name] = []

                for workout in workouts:
                    exercises_in_workout = exercise_instances.filter(workout_id=workout.id)
                    top_rep_workouts[exercise.exercise_name.name].extend(
                        [(workout, exercise) for exercise in exercises_in_workout[:1]])

    context = {
        'top_rep_workouts': top_rep_workouts,
        'query': query if query else '',
        'page_obj': page_obj,
    }

    return render(request, 'personal_records_by_reps.html', context=context)


@login_required
def workout_summary_calendar(request, year=None):
    if year is None:
        year = datetime.now().year
    else:
        year = int(year)

    user = request.user

    num_exercises = Exercise.objects.filter(athlete=user).count()

    num_workouts = Workout.objects.filter(athlete=user).count()

    num_visits = request.session.get(f'num_visits_{user.id}', 1)
    request.session[f'num_visits_{user.id}'] = num_visits + 1

    current_date = date(year, 1, 1)
    calendar_months = []

    for _ in range(12):
        workouts = Workout.objects.filter(athlete=user, date__year=current_date.year, date__month=current_date.month)
        month_days = []

        _, days_in_month = monthrange(current_date.year, current_date.month)
        starting_day = current_date.weekday()
        num_empty_cells = starting_day
        total_cells = num_empty_cells + days_in_month
        num_rows = total_cells // 7 + 1

        month_days.extend([('', False)] * num_empty_cells)

        for day in range(1, days_in_month + 1):
            workout_for_day = workouts.filter(date__year=current_date.year, date__month=current_date.month,
                                              date__day=day).first()
            is_marked = workout_for_day is not None
            workout_id = workout_for_day.id if is_marked else None
            month_days.append((day, is_marked, workout_id))

        # Add empty cells to complete the table rows
        remaining_cells = num_rows * 7 - len(month_days)
        month_days.extend([(None, False, None)] * remaining_cells)

        rows = []
        row = []
        for data in month_days:
            day = data[0]
            is_marked = data[1]
            workout_id = data[2] if len(data) > 2 else None
            row.append((day, is_marked, workout_id))
            if len(row) == 7:
                rows.append(row)
                row = []

        # Add the remaining row if it's not empty
        if row:
            rows.append(row)

        calendar_months.append({
            'month': current_date.strftime('%B'),
            'year': current_date.year,
            'rows': rows,
        })

        current_date = current_date.replace(day=1) + relativedelta(months=1)

    context = {
        'num_exercises': num_exercises,
        'num_workouts': num_workouts,
        'num_visits': num_visits,
        'calendar_months': calendar_months,
    }

    return render(request, 'workouts_calendar.html', context=context)
