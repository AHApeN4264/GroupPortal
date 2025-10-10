from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Вiary, Forum, Poll, Comment, UserMessage, Event, GradeForm, Grade, Question, Option
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from datetime import date 
import datetime
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta, datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Avg
from django.db import models
from functools import wraps
from django import forms
from django.core.paginator import Paginator
User = get_user_model()


def save_user_message(user, text, level="info"):
    if user.is_authenticated:
        UserMessage.objects.create(user=user, text=text, level=level)

@login_required
def message_all_users(request, id=None):
    role = get_user_role(request.user)

    if not request.user.is_staff and request.user.username.lower() != "andrey":
        messages.error(request, "У вас немає доступу до цієї сторінки.")
        return redirect('home', id=request.user.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            for user in User.objects.all():
                UserMessage.objects.create(
                    user=user,
                    text=f"Новина: {title}",
                    level="info"
                )
            messages.success(request, "Повідомлення успішно надіслано всім користувачам!")
        else:
            messages.error(request, "Заповніть поле з новиною!")


    return render(request, 'message-all-users.html', {
        'role': role
    })

def get_user_role(user):
    if not user.is_authenticated:
        return "Гість"
    if user.username.lower() == "andrey":
        return "Адміністратор"
    elif user.is_staff:
        return "Модератор"
    else:
        return "Користувач"

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            role = get_user_role(request.user)
            if role not in allowed_roles:
                messages.error(request, "У вас немає доступу до цієї сторінки.")
                return redirect('home', id=request.user.id)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def home(request, id=None):
    role = get_user_role(request.user)

    if not id or id in ['none', 'None']:
        user = None
    else:
        try:
            user = User.objects.get(id=int(id))
        except (User.DoesNotExist, ValueError):
            return redirect('home', id='none')

    return render(request, 'home.html', {
        'user': user,
        'role': role
    })

def calendar(request):
    role = get_user_role(request.user)
    events = Event.objects.all().order_by("date")

    return render(request, 'Calendar.html', {
        'role': role,
        'events': events,
        'today': date.today()
    })

@login_required
def add_event(request):
    role = get_user_role(request.user)
    if role not in ["Адміністратор", "Модератор"]:
        messages.error(request, "У вас немає прав для додавання подій.")
        return redirect("calendar")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        event_date = request.POST.get("date")
        if title and event_date:
            Event.objects.create(
                title=title,
                description=description,
                date=event_date,
                created_by=request.user
            )
            messages.success(request, "Подію додано!")
            return redirect("calendar")
    
    return render(request, 'add-event.html', {
        'role': role
    })

@login_required
def view_event(request, id):
    role = get_user_role(request.user)
    event = get_object_or_404(Event, id=id)
    comments = event.comments.all().order_by('-created_at')

    if request.method == "POST":
        text = request.POST.get("comment")
        photo = request.FILES.get("photo")
        if text:
            Comment.objects.create(
                event=event,
                author=request.user,
                text=text,
                photo=photo
            )
            messages.success(request, "Коментар додано!")
            return redirect("view-event", id=id)
        else:
            messages.error(request, "Коментар не може бути порожнім!")

    return render(request, "view-event.html", {
        "role": role,
        "event": event,
        "comments": comments
    })

@login_required
def create_quest_forum(request, id=None):
    role = get_user_role(request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        quest = request.POST.get('quest')

        if title and quest:
            Forum.objects.create(
                owner=request.user,
                title=title,
                quest=quest,
                is_approved=False
            )
            messages.success(request, "Питання успішно створено! Очікує на модерацію.")
            save_user_message(request.user, "Питання успішно створено! Очікує на модерацію.", "success")
            return redirect('home', id=request.user.id)

        else:
            messages.error(request, "Заповніть всі поля!")

    return render(request, 'create-quest-forum.html',{
        'role': role
    })

def view_all_questions(request):
    title_query = request.GET.get('title', '')
    questions = Forum.objects.filter(is_approved=True)

    if title_query:
        questions = questions.filter(title__icontains=title_query)

    questions = questions.order_by('-approved_at')

    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    messages_list = paginator.get_page(page_number)

    role = get_user_role(request.user)

    return render(request, 'view-all-questions.html', {
        'questions': messages_list, 
        'role': role,
        'title_query': title_query,
        'messages_list': messages_list,
    })

@login_required
def view_your_questions(request):
    role = get_user_role(request.user)

    user_questions = Forum.objects.filter(owner=request.user)

    return render(request, 'view-your-questions.html', {
        'questions': user_questions,
        'role': role
    })

def view_question(request, id):
    role = get_user_role(request.user)

    question = get_object_or_404(Forum, id=id)
    comments = question.comments.all().order_by('-created_at')

    if request.method == 'POST':
        text = request.POST.get('comment')
        photo = request.FILES.get('photo')
        if text:
            Comment.objects.create(
                question=question,
                author=request.user,
                text=text,
                photo=photo
            )
            messages.success(request, "Коментар додано!")
            return redirect('view-question', id=id)
        else:
            messages.error(request, "Коментар не може бути порожнім!")


    return render(request, 'view-question.html', {
        'question': question,
        'comments': comments,
        'role': role
    })

@login_required
def view_request_users(request):
    if not request.user.is_staff and request.user.username.lower() != "andrey":
        messages.error(request, "У вас немає доступу до цієї сторінки.")
        return redirect('home', id=request.user.id)

    questions = Forum.objects.filter(is_approved=False).order_by('-created_at')

    return render(request, 'view-request-users.html', {
        'questions': questions,
        'role': "Модератор" if request.user.is_staff else "Адміністратор"
    })

@login_required
def approve_question(request, id):
    q = get_object_or_404(Forum, id=id)
    if request.user.is_staff or request.user.username.lower() == "andrey":
        q.is_approved = True
        q.approved_at = timezone.now()
        q.save()
        messages.success(request, "Питання схвалено!")
        save_user_message(request.user, f"Питання схвалено! '{q.title}'", "success")

        UserMessage.objects.create(
            user=q.owner,
            text=f"Ваше питання '{q.title}' було схвалено модератором.",
            level="success"
        )
    return redirect('view-request-users')

@login_required
def reject_question(request, id):
    q = get_object_or_404(Forum, id=id)
    if request.user.is_staff or request.user.username.lower() == "andrey":
        question_title = q.title
        q.delete()
        messages.success(request, "Питання видалено!")
        save_user_message(request.user, f"Питання видалено! '{q.title}'", "success")

        UserMessage.objects.create(
            user=q.owner,
            text=f"Ваше питання '{question_title}' було відхилено модератором.",
            level="error"
        )
    return redirect('view-request-users')

@login_required
def delete_question(request, id):
    question = get_object_or_404(Forum, id=id, owner=request.user)
    question.delete()
    messages.success(request, "Питання успішно видалено")
    return redirect('view-all-questions')

@login_required
def delete_question_my(request, id):
    question = get_object_or_404(Forum, id=id, owner=request.user)
    question.delete()
    messages.success(request, "Питання успішно видалено")
    return redirect('view-your-questions')

@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if comment.author == request.user or request.user.role in ["Модератор", "Адміністратор"]:
        comment.delete()
        messages.success(request, "Коментар успішно видалено")
    else:
        messages.error(request, "У вас немає прав на видалення цього коментаря")
    return redirect('view-question', id=comment.question.id)

@login_required
def delete_message(request, id):
    msg = get_object_or_404(UserMessage, id=id, user=request.user)
    msg.delete()
    messages.success(request, "Повідомлення успішно видалено")
    return redirect('history')

@login_required
def delete_event(request, id):
    msg = get_object_or_404(Event, id=id)
    msg.delete()
    messages.success(request, "Повідомлення успішно видалено")
    return redirect('calendar')

def grade_delete(request, pk):
    grade_instance = get_object_or_404(Grade, pk=pk)

    role = get_user_role(request.user)
    if role not in ["Модератор", "Адміністратор"]:
        messages.error(request, "У вас немає доступу до цієї сторінки.")
        return redirect('grade')

    if request.method == "POST":
        grade_instance.delete()
        messages.success(request, f"Учень '{grade_instance.student_name}' видалений!")
        return redirect('grade-add')

    return redirect('grade')

@login_required
def delete_poll(request, id):
    poll = get_object_or_404(Poll, id=id)
    role = get_user_role(request.user)

    if poll.owner != request.user and role not in ["Модератор", "Адміністратор"]:
        messages.error(request, "У вас немає прав на видалення цього опитування.")
        return redirect('view-all-poll')

    poll.delete()
    messages.success(request, "Опитування успішно видалено!")
    return redirect('view-all-poll')

@login_required
def history(request):
    role = get_user_role(request.user)

    messages_qs = request.user.messages.all().order_by('-created_at')

    paginator = Paginator(messages_qs, 20)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)

    return render(request, 'history.html', {
        'role': role,
        'messages_list': messages_page,
    })

@login_required
def grade(request):
    role = get_user_role(request.user)

    grades_list = Grade.objects.all().order_by('student_name')
    paginator = Paginator(grades_list, 20)

    page_number = request.GET.get('page')
    grades = paginator.get_page(page_number)

    return render(request, 'grade.html', {
        'grades': grades,
        'role': role,
    })

@login_required
def grade_add(request):
    role = get_user_role(request.user)

    grades_list = Grade.objects.all().order_by('student_name')
    paginator = Paginator(grades_list, 10)

    page_number = request.GET.get('page')
    grades = paginator.get_page(page_number)

    if request.method == "POST" and 'add_student' in request.POST:
        new_student = Grade.objects.create(
            student_name="Новий учень",
            student_class="-",
            subject="-",
            grade=0
        )
        new_student.student_name = f"Новий учень {new_student.id}"
        new_student.save()
        messages.success(request, f"Учень '{new_student.student_name}' доданий!")
        return redirect('grade-add')

    return render(request, "grade-add.html", {
        "grades": grades,
        "role": role
    })

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student_name', 'student_class', 'subject', 'subject_text', 'grade']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'subject_text': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

@login_required
def grade_edit(request, pk):
    grade_instance = get_object_or_404(Grade, pk=pk)
    role = get_user_role(request.user)

    if not request.user.is_staff and request.user.username.lower() != "andrey":
        messages.error(request, "У вас немає доступу до цієї сторінки.")
        return redirect('grade')

    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade_instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"Учня '{form.cleaned_data['student_name']}' оновлено!")
            return redirect('grade-add')
    else:
        form = GradeForm(instance=grade_instance)

    return render(request, 'grade-edit.html', {
        'form': form,
        'grade': grade_instance,
        'role': role
    })

@login_required
def view_event(request, id):
    role = get_user_role(request.user)
    event = get_object_or_404(Event, id=id)
    comments = event.comments.all().order_by('-created_at')

    if request.method == "POST":
        text = request.POST.get("comment")
        photo = request.FILES.get("photo")
        if text:
            Comment.objects.create(
                event=event,
                author=request.user,
                text=text,
                photo=photo
            )
            messages.success(request, "Коментар додано!")
            return redirect("view-event", id=id)
        else:
            messages.error(request, "Коментар не може бути порожнім!")

    return render(request, "view-event.html", {
        "role": role,
        "event": event,
        "comments": comments
    })

@login_required
def create_poll(request):
    if not request.user.is_staff and request.user.username.lower() != "andrey":
        messages.error(request, "У вас немає доступу до цієї сторінки.")
        return redirect('home', id=request.user.id)
    
    role = get_user_role(request.user)
    if request.method == "POST":
        title = request.POST.get('title')
        if not title:
            messages.error(request, "Назва опитування обов'язкова!")
            return redirect('create_poll')

        poll = Poll.objects.create(owner=request.user, title=title)

        for i in range(1, 6):
            q_text = request.POST.get(f'quest{i}')
            if not q_text:
                continue
            question = Question.objects.create(poll=poll, text=q_text)

            for j in range(1, 4):
                opt_text = request.POST.get(f'q{i}_opt{j}')
                is_correct = request.POST.get(f'q{i}_correct') == str(j)
                Option.objects.create(question=question, text=opt_text, is_correct=is_correct)

        messages.success(request, "Опитування створено успішно!")
        return redirect('home', id=request.user.id)

    return render(request, 'create-poll.html', {
        'role': role,
        'role': "Модератор" if request.user.is_staff else "Адміністратор"
    })

@login_required
def edit_poll(request, id):
    poll = get_object_or_404(Poll, id=id)
    role = get_user_role(request.user)

    if poll.owner != request.user and role not in ["Модератор", "Адміністратор"]:
        messages.error(request, "У вас немає доступу до редагування цього опитування.")
        return redirect('home', id=request.user.id)

    if request.method == "POST":
        poll.title = request.POST.get('title')
        poll.save()

        for i, question in enumerate(poll.questions.all(), start=1):
            q_text = request.POST.get(f'quest{i}')
            if q_text:
                question.text = q_text
                question.save()

            correct_opt = request.POST.get(f'q{i}_correct')
            for j, option in enumerate(question.options.all(), start=1):
                opt_text = request.POST.get(f'q{i}_opt{j}')
                if opt_text:
                    option.text = opt_text
                    option.is_correct = (correct_opt == str(j))
                    option.save()

        messages.success(request, "Опитування оновлено успішно!")
        return redirect('view-all-poll')

    return render(request, 'edit-poll.html', {
        'poll': poll,
        'role': role,
    })

@login_required
def results_poll(request, id):
    poll = get_object_or_404(Poll, id=id)
    role = get_user_role(request.user)

    questions = poll.questions.all()
    total_votes = 0
    results = []

    for question in questions:
        for option in question.options.all():
            total_votes += getattr(option, 'votes', 0)

    for question in questions:
        option_stats = []
        for option in question.options.all():
            votes = getattr(option, 'votes', 0)
            percent = (votes / total_votes * 100) if total_votes > 0 else 0
            option_stats.append({
                'text': option.text,
                'votes': votes,
                'percent': round(percent, 2),
                'is_correct': option.is_correct
            })
        results.append({
            'question': question.text,
            'options': option_stats
        })

    return render(request, 'results-poll.html', {
        'poll': poll,
        'role': role,
        'results': results,
        'total_votes': total_votes
    })

def view_all_poll(request):
    role = get_user_role(request.user)
    title_query = request.GET.get('title', '')
    polls = Poll.objects.all()

    if title_query:
        polls = polls.filter(title__icontains=title_query)

    polls = polls.order_by('-created_at')

    paginator = Paginator(polls, 10)
    page_number = request.GET.get('page')
    polls_page = paginator.get_page(page_number)

    return render(request, 'view-all-poll.html', {
        'poll': polls_page,
        'role': role,
        'title_query': title_query,
        'messages_list': polls_page,
    })

@login_required
def view_poll(request, id):
    poll = get_object_or_404(Poll, id=id)
    role = get_user_role(request.user)

    questions = list(poll.questions.all())
    total_questions = len(questions)
    current_index = int(request.GET.get('q', 1))

    if not questions:
        return render(request, 'view-poll.html', {
            'poll': poll,
            'role': role,
            'no_questions': True
        })

    if current_index > total_questions:
        return redirect('poll-submitted', id=poll.id)

    current_question = questions[current_index - 1]

    if request.method == "POST":
        selected_option_id = request.POST.get("option")
        if selected_option_id:
            option = current_question.options.filter(id=selected_option_id).first()
            if option:
                option.votes += 1
                option.save()

            next_q = current_index + 1
            return redirect(f"{request.path}?q={next_q}")

    return render(request, 'view-poll.html', {
        'poll': poll,
        'role': role,
        'question': current_question,
        'current_index': current_index,
        'total_questions': total_questions,
    })

@login_required
def poll_submitted(request, id):
    poll = get_object_or_404(Poll, id=id)
    role = get_user_role(request.user)

    return render(request, 'poll-submitted.html', {
        'poll': poll,
        'role': role,
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        surname = request.POST.get('surname')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Користувач з ім'ям '{username}' вже існує")
            return redirect('register')
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, f"Користувач з номером телефону '{phone_number}' вже існує")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Користувач з email '{email}' вже існує")
            return redirect('register')

        user = User.objects.create(
            username=username,
            surname=surname,
            phone_number=phone_number,
            email=email,
            password=make_password(password)
        )

        auth_login(request, user)
        messages.success(request, "Користувача успішно створено та увійшли в акаунт")

        return redirect('home', id=request.user.id)

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        surname = request.POST.get('surname', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not surname or not phone_number or not email or not password:
            messages.error(request, "Будь ласка, заповніть все.")
            return render(request, 'login.html')
        errors = []
        user_by_username = User.objects.filter(username=username).first()
        if not user_by_username:
            errors.append("Ім'я користувача не знайдено.")
        user_by_surname = User.objects.filter(surname=surname).first()
        if not user_by_surname:
            errors.append("Прізвище користувача не знайдено.")
        user_by_phone = User.objects.filter(phone_number=phone_number).first()
        if not user_by_phone:
            errors.append("Номер телефону не знайдено.")
        user_by_email = User.objects.filter(email=email).first()
        if not user_by_email:
            errors.append("Електронну пошту не знайдено.")
        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'login.html')
        try:
            user = User.objects.get(username=username, surname=surname, phone_number=phone_number, email=email)
        except User.DoesNotExist:
            messages.error(request, "Користувача з такими комбінаціями даних не знайдено.")
            return render(request, 'login.html')
        if not check_password(password, user.password):
            messages.error(request, "Невірний пароль.")
            return render(request, 'login.html')
        auth_login(request, user)
        messages.success(request, "Ви увійшли в акаунт!")
        return redirect('home', id=request.user.id)
    return render(request, 'login.html')

def register_delete(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None
        if user:
            if check_password(password, user.password):
                user.delete()
                messages.success(request, "Користувача успішно видалено")
                return redirect('login')
            else:
                messages.error(request, "Невірний пароль")
        else:
            messages.error(request, "Користувач з такими даними не знайдений")

    return render(request, 'register-delete.html')
