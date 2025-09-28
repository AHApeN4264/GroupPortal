from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

# python manage.py makemigrations
# python manage.py migrate

class User(AbstractUser):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surname = models.CharField(max_length=150, null=True, blank=True)
    gmail = models.EmailField(max_length=254, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    grade = models.CharField(max_length=3, null=True, blank=True)
    subjects = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Студент: {self.user.username}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surname = models.CharField(max_length=150, null=True, blank=True)
    gmail = models.EmailField(max_length=254, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    
    subject = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Вчитель: {self.user.username}"
    
class ScheduleEntry(models.Model):
    DAY_CHOICES = [
        ('Понеділок', 'Понеділок'),
        ('Вівторок', 'Вівторок'),
        ('Середа', 'Середа'),
        ('Четвер', 'Четвер'),
        ("П'ятниця", "П'ятниця"),
    ]

    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    time = models.CharField(max_length=20)
    subject = models.CharField(max_length=100, blank=True)
    teacher = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.day} {self.time} - {self.subject}"


class Forum(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_owned",
        default=1
    )
    title = models.CharField(max_length=100)
    quest = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    question = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} on {self.question.title}"

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