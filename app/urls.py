from . import views
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView

def catch_all_redirect(request, path=None):
    if request.user.is_authenticated:
        return redirect('home', id=str(request.user.id))
    else:
        return redirect('home', id='none')

urlpatterns = [
    path('', lambda request: redirect('menu', id=request.user.id if request.user.is_authenticated else 'none')),
    path('register', views.register, name='register'),
    path('register-delete', views.register_delete, name='register-delete'),
    path('login', views.login, name='login'),
    path('login/student', views.login_student, name='login-student'),
    path('login/teacher', views.login_teacher, name='login-teacher'),
    path('logout/', LogoutView.as_view(next_page='/login'), name='logout'),
    path('home/<int:id>/', views.menu, name='home'),
    path('calendar', views.calendar, name='calendar'),
    path('add-event', views.add_event, name='add-event'),
    path('view-event/<int:id>', views.view_event, name='view-event'),
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
    path('approve-question/<int:id>/', views.approve_question, name='approve-question'),
    path('reject-question/<int:id>/', views.reject_question, name='reject-question'),
    path('history', views.history, name='history'),
    path('message-all-users', views.message_all_users, name='message-all-users'),
    path('grade', views.grade, name='grade'),
    path('role', views.role, name='role'),
    # path('schedule', views.schedule_view, name='schedule'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^(?P<path>.*)$', catch_all_redirect),
]
