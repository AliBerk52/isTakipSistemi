from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import (
    User, UserProfile, Project, ProjectMember, Task, TaskStatus,
    PasswordResetToken, Role, ActionLog, Comment, Department
)
from .forms import (
    RegisterForm, LoginForm, ProjectForm, TaskForm, CommentForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)
from .decorators import role_required

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def log_action(user, action: str):
    ActionLog.objects.create(user=user, action=action)


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def check_project_access(user, project):
    if user.is_staff:
        return
    if not ProjectMember.objects.filter(project=project, user=user).exists():
        raise PermissionDenied


# -------------------------------------------------------
# AUTH
# -------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()

            # En alt seviye rolü otomatik ata
            worker_role, _ = Role.objects.get_or_create(role_name='worker')
            user.base_role = worker_role
            user.save()

            UserProfile.objects.create(user=user)
            log_action(user, "Sisteme kayıt oldu")
            login(request, user)
            return redirect('project_list')
        

    return render(request, 'login.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        role_name = User.base_role.role_name if User.base_role else None

        if role_name == 'Admin':
            return redirect('admin_dashboard')
        elif role_name == 'Project Manager':
            return redirect('admin_project_list')
        else:
            return redirect('project_list')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        ip = get_client_ip(request)
        cache_key = f"login_fail_{ip}"
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            messages.error(request, f"Çok fazla başarısız giriş denemesi. {LOCKOUT_SECONDS // 60} dakika bekleyin.")
            return render(request, 'login.html', {'form': form, 'locked': True})

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Kutucuğun durumunu doğrudan HTML formundan (POST) okuyoruz:
            remember_me = request.POST.get('remember_me') == 'on'

            user = authenticate(request, username=username, password=password)
            if user:
                cache.delete(cache_key)
                login(request, user)
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 14)
                else:
                    request.session.set_expiry(0)
                log_action(user, "Sisteme giriş yaptı")
                return redirect('dashboard')
            else:
                cache.set(cache_key, attempts + 1, LOCKOUT_SECONDS)
                remaining = MAX_LOGIN_ATTEMPTS - (attempts + 1)
                messages.error(request, f"Kullanıcı adı veya şifre hatalı. Kalan deneme hakkı: {max(remaining, 0)}")

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, "Sistemden çıkış yaptı")
        logout(request)
    return redirect('login')


# -------------------------------------------------------
# ŞİFRE SIFIRLAMA
# -------------------------------------------------------

def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            PasswordResetToken.objects.filter(user=user).delete()
            token = secrets.token_urlsafe(48)
            PasswordResetToken.objects.create(user=user, token=token)
            reset_url = request.build_absolute_uri(f'/sifre-sifirla/{token}/')
            log_action(user, "Şifre sıfırlama isteği oluşturuldu")
            messages.info(request, f"[DEV] Sıfırlama linki: {reset_url}")
        except User.DoesNotExist:
            pass
        messages.success(request, "E-posta adresiniz sistemde kayıtlıysa sıfırlama bağlantısı gönderildi.")
        return redirect('login')

    return render(request, 'sifreDegistir.html', {'form': form})


def password_reset_confirm_view(request, token: str):
    reset_token = PasswordResetToken.objects.filter(token=token).first()
    if not reset_token:
        messages.error(request, "Geçersiz veya süresi dolmuş bağlantı.")
        return redirect('password_reset_request')

    if timezone.now() - reset_token.createdAt > timedelta(minutes=15):
        reset_token.delete()
        messages.error(request, "Bağlantının süresi dolmuş.")
        return redirect('password_reset_request')

    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = reset_token.user
        user.set_password(form.cleaned_data['new_password'])
        user.save()
        reset_token.delete()
        log_action(user, "Şifresini sıfırladı")
        messages.success(request, "Şifreniz başarıyla güncellendi.")
        return redirect('login')

    return render(request, 'sifreDegistir.html', {'form': form})


# -------------------------------------------------------
# DASHBOARD
# -------------------------------------------------------

@login_required
def dashboard_view(request):
    my_projects = ProjectMember.objects.filter(
        user=request.user
    ).select_related('project')

    my_tasks = Task.objects.filter(
        assigned_worker=request.user
    ).select_related('project', 'status').order_by('-created_at')[:10]

    return render(request, 'index.html', {
        'my_projects': my_projects,
        'my_tasks': my_tasks,
    })


# -------------------------------------------------------
# PROJE — CRUD + Toggle
# -------------------------------------------------------

@login_required
def project_list_view(request):
    memberships = ProjectMember.objects.filter(
        user=request.user
    ).select_related('project')
    return render(request, 'projeler.html', {'all_projects': projeler})

@login_required
def project_create_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        if not project.start_date:
            from django.utils import timezone
            project.start_date = timezone.now().date()
        project = form.save()

        # Seçilen proje sorumlusunu ekle
        manager_id = request.POST.get('project_admin')
        if manager_id:
            manager = User.objects.filter(pk=manager_id).first()
            pm_role, _ = Role.objects.get_or_create(role_name='Project Manager')
            if manager:
                ProjectMember.objects.get_or_create(
                    project=project, user=manager,
                    defaults={'role_in_project': pm_role}
                )

        # Oluşturan kişiyi de ekle (admin ise)
        if request.user != manager if manager_id else True:
            admin_role = Role.objects.filter(role_name='Admin').first()
            ProjectMember.objects.get_or_create(
                project=project, user=request.user,
                defaults={'role_in_project': admin_role}
            )

        log_action(request.user, f"Proje oluşturuldu: '{project.project_name}'")
        messages.success(request, "Proje başarıyla oluşturuldu.")
        return redirect('project_detail', pk=project.pk)

    users = User.objects.filter(is_active=True).select_related('base_role').order_by('username')
    return render(request, 'projeOlustur.html', {
        'form': form,
        'action': 'Yeni Proje Oluştur',
        'employees': users,
    })


@login_required
def project_detail_view(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    check_project_access(request.user, project)

    tasks = project.tasks.select_related('assigned_worker', 'status').order_by('-created_at')
    members = project.members.select_related('user', 'role_in_project')

    return render(request, 'projeArayuzu.html', {
        'project': project,
        'tasks': tasks,
        'members': members,
    })


@login_required
def project_update_view(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    check_project_access(request.user, project)

    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.user, f"Proje güncellendi: '{project.project_name}'")
        messages.success(request, "Proje güncellendi.")
        return redirect('project_detail', pk=pk)

    return render(request, 'projeArayuzu.html', {'form': form, 'action': 'Güncelle', 'project': project})


@login_required
def project_list_view(request):
    if request.user.is_staff or (
        request.user.base_role and
        request.user.base_role.role_name == 'Admin'
    ):
        projeler = Project.objects.all().order_by('-start_date')
    else:
        projeler = Project.objects.filter(
            members__user=request.user
        ).order_by('-start_date')

    return render(request, 'projeler.html', {'projeler': projeler})


@login_required
def project_toggle_view(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    check_project_access(request.user, project)

    if request.method == 'POST':
        project.is_active = not project.is_active
        project.save()
        durum = "açıldı" if project.is_active else "kapatıldı"
        log_action(request.user, f"Proje {durum}: '{project.project_name}'")
        messages.success(request, f"Proje {durum}.")

    return redirect('project_detail', pk=pk)


# -------------------------------------------------------
# GÖREV — CRUD
# -------------------------------------------------------

@login_required
def task_create_view(request, project_pk: int):
    project = get_object_or_404(Project, pk=project_pk)
    check_project_access(request.user, project)

    form = TaskForm(request.POST or None, project=project)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.save()
        log_action(request.user, f"Görev oluşturuldu: '{task.task_name}' (Proje: {project.project_name})")
        messages.success(request, "Görev oluşturuldu.")
        return redirect('project_detail', pk=project_pk)

    return render(request, 'gorevOlustur.html', {'form': form, 'project': project, 'action': 'Oluştur'})


@login_required
def task_detail_view(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    check_project_access(request.user, task.project)

    comments = task.comments.select_related('user').order_by('created_at')
    comment_form = CommentForm()

    return render(request, 'islerim.html', {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def task_update_view(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    check_project_access(request.user, task.project)

    form = TaskForm(request.POST or None, instance=task, project=task.project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.user, f"Görev güncellendi: '{task.task_name}'")
        messages.success(request, "Görev güncellendi.")
        return redirect('task_detail', pk=pk)

    return render(request, 'islerim.html', {'form': form, 'project': task.project, 'action': 'Güncelle', 'task': task})


@login_required
def task_delete_view(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    check_project_access(request.user, task.project)

    if request.method == 'POST':
        project_pk = task.project.pk
        name = task.task_name
        task.delete()
        log_action(request.user, f"Görev silindi: '{name}'")
        messages.success(request, "Görev silindi.")
        return redirect('project_detail', pk=project_pk)

    return render(request, 'islerim.html', {'task': task})


# -------------------------------------------------------
# YORUM
# -------------------------------------------------------

@login_required
def comment_create_view(request, task_pk: int):
    task = get_object_or_404(Task, pk=task_pk)
    check_project_access(request.user, task.project)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            log_action(request.user, f"Göreve yorum ekledi: '{task.task_name}'")

    return redirect('task_detail', pk=task_pk)


@login_required
def comment_delete_view(request, pk: int):
    comment = get_object_or_404(Comment, pk=pk)
    task_pk = comment.task.pk

    if comment.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        log_action(request.user, f"Yorum silindi (Görev: '{comment.task.task_name}')")
        comment.delete()
        messages.success(request, "Yorum silindi.")

    return redirect('task_detail', pk=task_pk)


# -------------------------------------------------------
# YÖNETİM PANELİ
# -------------------------------------------------------

@login_required
@role_required(['Admin'])
def admin_dashboard_view(request):
    projects = Project.objects.prefetch_related('members').order_by('-start_date')
    context = {
        'all_projects': projects,
        'user_count': User.objects.count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'project_count': projects.count(),
        'task_count': Task.objects.count(),
        'recent_logs': ActionLog.objects.select_related('user').order_by('-timestamp')[:20],
    }
    return render(request, 'yonetici.html', context)


@login_required
@role_required(['Admin'])
def admin_user_list_view(request):
    users = User.objects.select_related('base_role', 'membership').order_by('username')
    return render(request, 'calisanlar.html', {'users': users})


@login_required
@role_required(['Admin'])
def admin_user_toggle_view(request, pk: int):
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, "Kendi hesabınızı pasif yapamazsınız.")
        return redirect('admin_user_list')

    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        durum = "aktifleştirildi" if user.is_active else "pasifleştirildi"
        log_action(request.user, f"Kullanıcı {durum}: '{user.username}'")
        messages.success(request, f"Kullanıcı {durum}.")

    return redirect('admin_user_list')


@login_required
@role_required(['Admin'])
def admin_project_list_view(request):
    projects = Project.objects.prefetch_related('members').order_by('-start_date')
    return render(request, 'projeAdmini.html', {'projects': projects})


@login_required
@role_required(['Admin'])
def admin_log_view(request):
    logs = ActionLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'log.html', {'logs': logs})


@login_required
@role_required(['Admin'])
def team_create_view(request, project_pk: int):
    project = get_object_or_404(Project, pk=project_pk)
    all_users = User.objects.filter().select_related('base_role')
    current_members = project.members.values_list('user_id', flat=True)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        user = get_object_or_404(User, pk=user_id)
        role = Role.objects.filter(pk=role_id).first()
        ProjectMember.objects.get_or_create(
            project=project, user=user,
            defaults={'role_in_project': role}
        )
        log_action(request.user, f"Takıma eklendi: '{user.username}' → '{project.project_name}'")
        messages.success(request, f"{user.username} takıma eklendi.")
        return redirect('team_create', project_pk=project_pk)

    return render(request, 'takimOlustur.html', {
        'project': project,
        'all_users': all_users,
        'current_members': current_members,
        'roles': Role.objects.all(),
    })

@login_required
def project_delete_view(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    check_project_access(request.user, project)

    if request.method == 'POST':
        name = project.project_name
        project.delete()
        log_action(request.user, f"Proje silindi: '{name}'")
        messages.success(request, "Proje silindi.")
        return redirect('project_list')

    return render(request, 'projeArayuzu.html', {'project': project})


@login_required
@role_required(['Admin'])
def admin_user_edit_view(request, pk: int):
    emp = get_object_or_404(User, pk=pk)
    roles = Role.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        emp.email = request.POST.get('email', emp.email)

        role_id = request.POST.get('role_id')
        emp.base_role = Role.objects.filter(pk=role_id).first() if role_id else None

        dept_id = request.POST.get('department_id')
        emp.department = Department.objects.filter(pk=dept_id).first() if dept_id else None

        emp.is_active = request.POST.get('is_active') == '1'
        emp.save()

        log_action(request.user, f"Kullanıcı düzenlendi: '{emp.username}'")
        messages.success(request, f"{emp.username} güncellendi.")
        return redirect('admin_user_list')

    return render(request, 'kullaniciDuzenle.html', {
        'emp': emp,
        'roles': roles,
        'departments': departments,
    })


def admin_user_tasks_view(request, pk: int):
    emp = get_object_or_404(User, pk=pk)
    tasks = Task.objects.filter(
        assigned_worker=emp
    ).select_related('project', 'status').order_by('-created_at')

    completed_count = tasks.filter(status__status_name='Tamamlandı').count()

    return render(request, 'kullaniciGorevleri.html', {
        'emp': emp,
        'tasks': tasks,
        'completed_count': completed_count,
    })
