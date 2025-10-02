from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Вiary, Forum, Comment, UserMessage, Event, GradeForm, Grade
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

    role = get_user_role(request.user)

    return render(request, 'view-all-questions.html', {
        'questions': questions,
        'role': role,
        'title_query': title_query,
    })

@login_required
def view_your_questions(request):
    role = get_user_role(request.user)

    user_questions = Forum.objects.filter(owner=request.user)

    return render(request, 'view-your-questions.html', {
        'questions': user_questions,
        'role': role
    })

@login_required
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

@login_required
def history(request):
    role = get_user_role(request.user)
    
    messages_list = request.user.messages.all().order_by('-created_at')
    
    return render(request, 'history.html', {
        'role': role,
        'messages_list': messages_list
    })

@login_required
def role(request):
    role = get_user_role(request.user)
    
    
    return render(request, 'history.html', {
        'role': role,
    })

def grade(request):
    role = get_user_role(request.user)
    
    grades = Grade.objects.all().order_by('student_name')

    return render(request, 'grade.html', {
        'grades': grades,
        'role': role,
    })

def grade_add(request):
    role = get_user_role(request.user)

    grades = Grade.objects.all().order_by('student_name')

    if request.method == "POST" and 'add_student' in request.POST:
        new_student = Grade.objects.create(
            student_name="Новий учень",
            student_class="Поки не в якому",
            subject="Нема уроків поки",
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

        Student.objects.create(
            user=user,
            surname=surname
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

def login_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'student'):
            auth_login(request, user)
            return redirect('home', args=[user.username])
        messages.error(request, "Невірний логін або пароль")
    return render(request, 'login-student.html')

def login_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        surname = request.POST.get('surname')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'teacher'):
            auth_login(request, user)
            return redirect(reverse('home', args=[user.username]))
        messages.error(request, "Невірний логін або пароль")
    return render(request, 'login-teacher.html')

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
