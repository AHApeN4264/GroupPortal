from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Вiary, Student, Teacher, Forum, Comment, UserMessage, ScheduleEntry
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

User = get_user_model()


def save_user_message(user, text, level="info"):
    if user.is_authenticated:
        UserMessage.objects.create(user=user, text=text, level=level)

@login_required
def message_all_users(request, id=None):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"

    if not request.user.is_staff and request.user.username.lower() != "andrey":
        messages.error(request, "У вас немає доступу до цієї сторінки.")
        return redirect('home', id=request.user.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            for user in User.objects.all():
                UserMessage.objects.create(
                    user=user,
                    text=f"новина: {title}",
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

def menu(request, id=None):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"

    if id == 'none' or id is None:
        user = None
    else:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return redirect('menu_none')
        
    return render(request, 'menu.html', {
        'user': user,
        'role': role
        })

@login_required
def create_quest_forum(request, id=None):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"

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

    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"

    return render(request, 'view-all-questions.html', {
        'questions': questions,
        'role': role,
        'title_query': title_query,
    })


@login_required
def view_your_questions(request):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"

    user_questions = Forum.objects.filter(owner=request.user)

    return render(request, 'view-your-questions.html', {
        'questions': user_questions,
        'role': role
    })


@login_required
def view_question(request, id):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"

    question = get_object_or_404(Forum, id=id)
    comments = question.comments.all().order_by('-created_at')

    if request.method == 'POST':
        text = request.POST.get('comment')
        if text:
            Comment.objects.create(
                question=question,
                author=request.user,
                text=text
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
def history(request):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"
    
    messages_list = request.user.messages.all().order_by('-created_at')
    
    return render(request, 'history.html', {
        'role': role,
        'messages_list': messages_list
    })

@login_required
def role(request):
    role = "Користувач"
    if request.user.is_authenticated:
        if request.user.username.lower() == "andrey":
            role = "Адміністратор"
        elif request.user.is_staff:
            role = "Модератор"
    
    
    return render(request, 'history.html', {
        'role': role,
    })

# @get_user_role
def grade(request):
    
    return render(request, 'grade.html', {
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Користувач з ім'ям '{username}' вже існує")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Користувач з email '{email}' вже існує")
            return redirect('register')

        user = User.objects.create(
            username=username,
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
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not surname or not email or not password:
            messages.error(request, "Будь ласка, заповніть все.")
            return render(request, 'login.html')
        errors = []
        user_by_username = User.objects.filter(username=username).first()
        if not user_by_username:
            errors.append("Ім'я користувача не знайдено.")
        user_by_phone = User.objects.filter(phone_number=surname).first()
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
            user = User.objects.get(username=username, phone_number=surname, email=email)
        except User.DoesNotExist:
            messages.error(request, "Користувача з такими комбінаціями даних не знайдено.")
            return render(request, 'login.html')
        if not check_password(password, user.password):
            messages.error(request, "Невірний пароль.")
            return render(request, 'login.html')
        auth_login(request, user)
        return redirect(reverse('home', args=[user.username]))
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
