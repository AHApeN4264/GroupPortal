from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django import forms
import app.models as app_models

# python manage.py makemigrations
# python manage.py migrate

class User(AbstractUser):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    surname = models.CharField(max_length=150, null=True, blank=True)
    gmail = models.EmailField(max_length=254, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=[
            ('Користувач', 'користувач'),
            ('Модератор', 'модератор'),
            ('Адміністратор', 'адміністратор'),
        ],
        default='Користувач',
    )
    role_user= models.CharField(
        max_length=20,
        choices=[
            ('Вчитель', 'вчитель'),
            ('Студент', 'студент'),
        ],
        default='Студент',
    )
    
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.date})"

class Forum(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_owned",
        default=1
    )
    photo = models.ImageField(null=True, blank=True, upload_to='photos/')
    title = models.CharField(max_length=100)
    quest = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="poll_owned"
    )
    photo = models.ImageField(null=True, blank=True, upload_to='photos/')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    votes = models.PositiveIntegerField(default=0)

class Comment(models.Model):
    photo = models.ImageField(null=True, blank=True, upload_to='photos/')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    question = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.event:
            return f"{self.author.username} on {self.event.title}"
        if self.question:
            return f"{self.author.username} on {self.question.title}"
        return f"{self.author.username}"
    
class Grade(models.Model):
    student_name = models.CharField(max_length=50)
    student_class = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    subject_text = models.CharField(
        max_length=50,
        default='-'
    )
    subject = models.CharField(
        max_length=50,
        choices=[
            ('-', '-'),
            ('Українська мова', 'Українська мова'),
            ('Українська література', 'Українська література'),
            ('Математика', 'Математика'),
            ('Біологія', 'Біологія'),
            ('Мистецтво', 'Мистецтво'),
            ('Історія України', 'Історія України'),
            ('Всесвітня історія', 'Всесвітня історія'),
            ('Основи правознавства', 'Основи правознавства'),
            ('Алгебра', 'Алгебра'),
            ('Геометрія', 'Геометрія'),
            ('Фізична культура', 'Фізична культура'),
            ('Інформатика', 'Інформатика'),
            ('Англійська мова', 'Англійська мова'),
            ('Виховна година', 'Виховна година'),
            ('Хімія', 'Хімія'),
            ('Зарубіжна література', 'Зарубіжна література'),
            ('Фізика', 'Фізика'),
            ('Географія', 'Географія'),
            ('Основи здоров’я', 'Основи здоров’я'),
            ('Трудове навчання', 'Трудове навчання'),
        ],
        default='-',
    )

    def __str__(self):
        return f"{self.student_name} ({self.student_class}) – {self.subject}: {self.grade}"

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student_name', 'student_class', 'subject', 'grade', 'created_at']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'created_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class Вiary(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_bookings",
        default=1
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_bookings"
    )
    title = models.CharField(
        max_length=200,
        default='Немає назви',
    )
    description = models.TextField(
        default='Немає опису',
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('В продажі', 'в продажі'),
            ('Продано', 'продано'),
        ],
        default='В продажі',
    )
    photo = models.ImageField(upload_to='media/', null=True, blank=True)
    first_data = models.DateField(auto_now_add=True, null=True, blank=True)
    room = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()

class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    level = models.CharField(max_length=20, default="info")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}"

class Project(models.Model): #Клас самого проекту
    author = models.ForeignKey(app_models.User, on_delete=models.CASCADE) #Користувач, що створив цей проект
    name = models.CharField(max_length=32) #Ім'я проекту
    description = models.TextField() #Опис проекту
    main_file = models.FileField(upload_to="projects_media") #Сам проект (один файл або архів)

    def __str__(self): return f"{self.author.username}: {self.name}"


class DopFile(models.Model): #Клас додаткових файлів до проекту (скріншотів, відео, тощо)
    project = models.ForeignKey(Project, on_delete=models.CASCADE) #Проект, до якого автор прикріпрює додатковий файл
    file = models.FileField(upload_to="projects_media") #Сам додатковий файл
    description = models.TextField(null=True, blank=True, max_length=64) #Опис до файлу

    def __str__(self): return f"Додатковий файл до {self.project.name}"
