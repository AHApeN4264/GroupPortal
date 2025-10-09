from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import portfolio.models as models


def all_projects(request): #Подивитися проекти усіх учнів
    paginator = Paginator(models.Project.objects.all(), 10)
    page_num = request.GET.get("page")
    return render(request, "portfolio/all_projects.html", {"projects":paginator.get_page(page_num)})

@login_required
def my_projects(request): #Подивитися портфоліо(проекти) даного учня
    return render(request, "portfolio/my_projects.html", {"projects":models.Project.objects.filter(author=request.user)})

def detail_project(request, project_id): #Подивитися деталі конкретного проекту
    if models.Project.objects.filter(id=project_id).exists():
        return render(request, "portfolio/detail_project.html", {"project":models.Project.objects.get(id=project_id),
                                                            "dopfiles":models.DopFile.objects.filter(project=project_id)})
    else:
        return redirect("portfolio:all_projects")


@login_required
def load_project(request): #Завантаження нового проекту
    if request.method == "GET":
        return render(request, "portfolio/load_project.html")
    elif request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        main_file = request.FILES["main_file"]

        new_project = models.Project.objects.create(author=request.user, name=name, description=description,
                                                    main_file=main_file)
        new_project.save()

        return redirect("portfolio:my_projects")

@login_required
def redact_project(request, project_id): #Редагування проекту
    if request.method == "GET":
        if models.Project.objects.filter(id=project_id).exists():
            return render(request, "portfolio/redact_project.html", {"project":models.Project.objects.get(id=project_id)})
        else:
            return redirect("portfolio:my_projects")
    elif request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        main_file = request.FILES.get("main_file")

        if not models.Project.objects.filter(id=project_id).exists(): return redirect("portfolio:my_projects")
        project = models.Project.objects.get(id=project_id)
        project.name = name
        project.description = description
        if main_file != None: project.main_file = main_file
        project.save()

        return redirect("portfolio:my_projects")

@login_required
def delete_project(request, project_id): #Видалення проекту
    if models.Project.objects.filter(id=project_id).exists():
        project = models.Project.objects.get(id=project_id)
        if request.user == project.author:
            project.delete()
    return redirect("portfolio:my_projects")


@login_required
def add_dopfile(request, project_id): #Додавання додаткового файлу до проекту
    if request.method == "POST":
        if models.Project.objects.filter(id=project_id).exists():
            project = models.Project.objects.get(id=project_id)
            file = request.FILES.get("file")
            if file != None:
                new_dopfile = models.DopFile.objects.create(project=project, file=file,
                                                            description=request.POST.get("description"))
                new_dopfile.save()
    return redirect("portfolio:my_projects")

@login_required
def delete_dopfile(requets, dopfile_id): #Видалення додаткового файлу у проекта
    if models.DopFile.objects.filter(id=dopfile_id).exists():
        dopfile = models.DopFile.objects.get(id=dopfile_id)
        if requets.user == dopfile.project.author:
            dopfile.delete()
    return redirect("portfolio:my_projects")
