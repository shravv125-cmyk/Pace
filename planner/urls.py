from django.contrib import admin
from django.urls import path
from planner import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",views.index,name='home'),
    path("landing",views.landing,name='landing'),
    path("userLogin",views.userLogin,name='login'),
    path("register",views.register,name='register'),
    path("dashboard",views.dashboard,name='dashboard'),
    path('subjects', views.subjects, name='subjects'),
    path("subjects/<int:user_slug_id>/",views.subject_detail,name="subject_detail"),
    path('task/toggle/<int:task_id>/', views.toggle_task_completion, name='toggle_task_completion'),
    path('study-log/', views.study_log_view, name='study_log'),
    path("userLogout",views.userLogout,name='logout'),
]

