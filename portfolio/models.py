from django.db import models
import app.models as app_models


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
