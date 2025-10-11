from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from . import views

def catch_all_redirect(request, path=None):
    if request.user.is_authenticated:
        return redirect('home', id=request.user.id)
    return redirect('home', id='none')


urlpatterns = [
    path('', lambda request: redirect('home', id=request.user.id if request.user.is_authenticated else 'none')),

    # Аутентификация
    path('register', views.register, name='register'),
    path('register-delete', views.register_delete, name='register-delete'),
    path('login', views.login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/login'), name='logout'),

    # Главная страница
    path('home/<str:id>/', views.home, name='home'),

    # Календарь и события
    path('calendar', views.calendar, name='calendar'),
    path('add-event', views.add_event, name='add-event'),
    path('view-event/<int:id>/', views.view_event, name='view-event'),

    # Вопросы, форумы и удаление
    path('create-quest-forum', views.create_quest_forum, name='create-quest-forum'),
    path('view-all-questions', views.view_all_questions, name='view-all-questions'),
    path('view-your-questions', views.view_your_questions, name='view-your-questions'),
    path('view-question/<int:id>', views.view_question, name='view-question'),
    path('view-request-users', views.view_request_users, name='view-request-users'),
    path('delete-question/<int:id>/', views.delete_question, name='delete-question'),
    path('delete-question-my/<int:id>/', views.delete_question_my, name='delete-question-my'),
    path('delete-message/<int:id>/', views.delete_message, name='delete-message'),
    path('delete-comment/<int:id>/', views.delete_comment, name='delete-comment'),
    path('delete-event/<int:id>/', views.delete_event, name='delete-event'),

    # Оценки
    path("grade/<int:pk>/delete/", views.grade_delete, name="grade_delete"),
    path('grade', views.grade, name='grade'),
    path('grade-add', views.grade_add, name='grade-add'),
    path("grade/<int:pk>/edit/", views.grade_edit, name="grade_edit"),

    # Опросы
    path('delete-poll/<int:id>/', views.delete_poll, name='delete-poll'),
    path('approve-question/<int:id>/', views.approve_question, name='approve-question'),
    path('reject-question/<int:id>/', views.reject_question, name='reject-question'),
    path('history', views.history, name='history'),
    path('message-all-users', views.message_all_users, name='message-all-users'),
    path('create-poll', views.create_poll, name='create-poll'),
    path('edit-poll/<int:id>', views.edit_poll, name='edit-poll'),
    path('view-all-poll', views.view_all_poll, name='view-all-poll'),
    path('view-poll/<int:id>', views.view_poll, name='view-poll'),
    path('poll-submitted/<int:id>', views.poll_submitted, name='poll-submitted'),
    path('results-poll/<int:id>', views.results_poll, name='results-poll'),

    # Проекты / портфолио (без namespace)
    path("all_projects/", views.all_projects, name="all_projects"),
    path("my_projects/", views.my_projects, name="my_projects"),
    path("load_project/", views.load_project, name="load_project"),
    path("detail_project/<int:project_id>/", views.detail_project, name="detail_project"),
    path("redact_project/<int:project_id>/", views.redact_project, name="redact_project"),
    path("delete_project/<int:project_id>/", views.delete_project, name="delete_project"),
    path("add_dopfile/<int:project_id>/", views.add_dopfile, name="add_dopfile"),
    path("delete_dopfile/<int:dopfile_id>/", views.delete_dopfile, name="delete_dopfile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^(?P<path>.*)$', catch_all_redirect),
]
