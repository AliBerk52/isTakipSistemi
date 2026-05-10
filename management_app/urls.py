from django.urls import path
from django.contrib.auth import views as auth_views # E-posta ve şifre sıfırlama için eklendi
from . import views

urlpatterns = [
    # -------------------------------------------------------
    # AUTH — Kayıt / Giriş / Çıkış
    # -------------------------------------------------------
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # -------------------------------------------------------
    # AUTH — Şifre Sıfırlama (Django Hazır Sistemine Geçirildi)
    # -------------------------------------------------------
    path('sifremi-unuttum/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), 
         name='password_reset'),
         
    path('sifremi-unuttum/mail-gonderildi/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),
         
    path('sifre-sifirla/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('sifre-sifirla/basarili/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),

    # -------------------------------------------------------
    # DASHBOARD (Ana Sayfa)
    # -------------------------------------------------------
    path('', views.dashboard_view, name='dashboard'),

    # -------------------------------------------------------
    # PROJE — CRUD + Toggle
    # -------------------------------------------------------
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update_view, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='project_delete'),
    path('projects/<int:pk>/toggle/', views.project_toggle_view, name='project_toggle'),

    # -------------------------------------------------------
    # GÖREV (TASK) — CRUD
    # -------------------------------------------------------
    # Görev oluştururken hangi projeye ait olduğunu bilmemiz gerektiği için URL'de project_pk taşıyoruz
    path('projects/<int:project_pk>/tasks/create/', views.task_create_view, name='task_create'),

    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update_view, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),

    # -------------------------------------------------------
    # YORUM (COMMENT)
    # -------------------------------------------------------
    path('tasks/<int:task_pk>/comments/create/', views.comment_create_view, name='comment_create'),
    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),

    # -------------------------------------------------------
    # YÖNETİM PANELİ (Admin Only)
    # -------------------------------------------------------
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_user_list_view, name='admin_user_list'),
    path('admin-panel/users/<int:pk>/toggle/', views.admin_user_toggle_view, name='admin_user_toggle'),
    path('admin-panel/projects/', views.admin_project_list_view, name='admin_project_list'),
    path('admin-panel/logs/', views.admin_log_view, name='admin_log'),

    path('yonetim/projeler/<int:project_pk>/takim/', views.team_create_view, name='team_create'),

    path('admin-panel/users/<int:pk>/edit/', views.admin_user_edit_view, name='admin_user_edit'),

    path('admin-panel/users/<int:pk>/tasks/', views.admin_user_tasks_view, name='admin_user_tasks'),
]