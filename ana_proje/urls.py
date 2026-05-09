"""
URL configuration for ana_proje project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.urls import path
from . import views

urlpatterns = [

    # ---- AUTH ----
    path('kayit/', views.register_view, name='register'),
    path('giris/', views.login_view, name='login'),
    path('cikis/', views.logout_view, name='logout'),
    path('sifre-sifirla/', views.password_reset_request_view, name='password_reset_request'),
    path('sifre-sifirla/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # ---- DASHBOARD ----
    path('', views.dashboard_view, name='dashboard'),

    # ---- PROJE ----
    path('projeler/', views.project_list_view, name='project_list'),
    path('projeler/olustur/', views.project_create_view, name='project_create'),
    path('projeler/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('projeler/<int:pk>/duzenle/', views.project_update_view, name='project_update'),
    path('projeler/<int:pk>/sil/', views.project_delete_view, name='project_delete'),
    path('projeler/<int:pk>/toggle/', views.project_toggle_view, name='project_toggle'),

    # ---- GÖREV ----
    path('projeler/<int:project_pk>/gorev/olustur/', views.task_create_view, name='task_create'),
    path('gorevler/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('gorevler/<int:pk>/duzenle/', views.task_update_view, name='task_update'),
    path('gorevler/<int:pk>/sil/', views.task_delete_view, name='task_delete'),

    # ---- YORUM ----
    path('gorevler/<int:task_pk>/yorum/', views.comment_create_view, name='comment_create'),
    path('yorumlar/<int:pk>/sil/', views.comment_delete_view, name='comment_delete'),

    # ---- YÖNETİM PANELİ ----
    path('yonetim/', views.admin_dashboard_view, name='admin_dashboard'),
    path('yonetim/kullanicilar/', views.admin_user_list_view, name='admin_user_list'),
    path('yonetim/kullanicilar/<int:pk>/toggle/', views.admin_user_toggle_view, name='admin_user_toggle'),
    path('yonetim/projeler/', views.admin_project_list_view, name='admin_project_list'),
    path('yonetim/loglar/', views.admin_log_view, name='admin_log'),
]
