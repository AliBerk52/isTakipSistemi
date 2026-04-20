from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.cache import cache
import secrets

from .models import (
    User, UserProfile, Project, ProjectMember, Task, TaskStatus,
    Comment, ActionLog, PasswordResetToken, Role
)
from .forms import (
    RegisterForm, LoginForm, ProjectForm, TaskForm, CommentForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)
from .decorators import role_required

# -------------------------------------------------------
# Brute force ayarları
# -------------------------------------------------------
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 dakika


# -------------------------------------------------------
# Yardımcı fonksiyonlar
# -------------------------------------------------------

def log_action(user, action: str):
    """Her önemli işlemi ActionLog'a yazar."""
    ActionLog.objects.create(user=user, action=action)


def get_client_ip(request) -> str:
    """Gerçek istemci IP'sini döner (proxy arkası dahil)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def check_project_access(user, project):
    """Kullanıcının projeye erişim hakkı yoksa PermissionDenied fırlatır."""
    if user.is_staff:
        return
    if not ProjectMember.objects.filter(project=project, user=user).exists():
        raise PermissionDenied


# -------------------------------------------------------
# AUTH — Kayıt / Giriş / Çıkış
# -------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        UserProfile.objects.create(user=user)
        log_action(user, "Sisteme kayıt oldu")
        messages.success(request, "Kayıt başarılı. Giriş yapabilirsiniz.")
        return redirect('login')

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        ip = get_client_ip(request)
        cache_key = f"login_fail_{ip}"
        attempts = cache.get(cache_key, 0)

        # Brute force kilidi
        if attempts >= MAX_LOGIN_ATTEMPTS:
            messages.error(
                request,
                f"Çok fazla başarısız giriş denemesi. {LOCKOUT_SECONDS // 60} dakika bekleyin."
            )
            return render(request, 'auth/login.html', {'form': form, 'locked': True})

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)
            if user:
                cache.delete(cache_key)  # Başarılı girişte sayacı sıfırla
                login(request, user)

                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 14)  # 14 gün
                else:
                    request.session.set_expiry(0)  # Tarayıcı kapanınca biter

                log_action(user, "Sisteme giriş yaptı")
                return redirect('dashboard')
            else:
                # Başarısız denemede sayacı artır
                cache.set(cache_key, attempts + 1, LOCKOUT_SECONDS)
                remaining = MAX_LOGIN_ATTEMPTS - (attempts + 1)
                messages.error(
                    request,
                    f"Kullanıcı adı veya şifre hatalı. Kalan deneme hakkı: {max(remaining, 0)}"
                )

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, "Sistemden çıkış yaptı")
        logout(request)
    return redirect('login')


# -------------------------------------------------------
# AUTH — Şifre Sıfırlama
# -------------------------------------------------------

def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            # Eski tokenları temizle
            PasswordResetToken.objects.filter(user=user).delete()
            token = secrets.token_urlsafe(48)
            PasswordResetToken.objects.create(user=user, token=token)
            # Gerçek projede: send_mail() ile gönder
            reset_url = request.build_absolute_uri(f'/sifre-sifirla/{token}/')
            log_action(user, "Şifre sıfırlama isteği oluşturuldu")
            # TODO: E-posta gönderimi eklenecek
            # Geliştirme aşamasında URL'yi mesaj olarak göster
            messages.info(request, f"[DEV] Sıfırlama linki: {reset_url}")
        except User.DoesNotExist:
            pass  # Kullanıcı bulunamasa da aynı yanıtı ver — kullanıcı sızdırma

        # Her durumda aynı mesajı göster (user enumeration koruması)
        messages.success(
            request,
            "E-posta adresiniz sistemde kayıtlıysa sıfırlama bağlantısı gönderildi."
        )
        return redirect('login')

    return render(request, 'auth/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, token: str):
    reset_token = PasswordResetToken.objects.filter(token=token).first()
    if not reset_token:
        messages.error(request, "Geçersiz veya süresi dolmuş bağlantı.")
        return redirect('password_reset_request')

    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = reset_token.user
        user.set_password(form.cleaned_data['new_password'])
        user.save()
        reset_token.delete()
        log_action(user, "Şifresini sıfırladı")
        messages.success(request, "Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.")
        return redirect('login')

    return render(request, 'auth/password_reset_confirm.html', {'form': form})


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

    return render(request, 'dashboard.html', {
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
    return render(request, 'projects/list.html', {'memberships': memberships})


@login_required
def project_create_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save()
        # Oluşturan kişiyi otomatik olarak PM rolüyle ekle
        pm_role = Role.objects.filter(role_name='Project Manager').first()
        ProjectMember.objects.create(
            project=project,
            user=request.user,
            role_in_project=pm_role
        )
        log_action(request.user, f"Proje oluşturuldu: '{project.project_name}'")
        messages.success(request, "Proje başarıyla oluşturuldu.")
        return redirect('project_detail', pk=project.pk)

    return render(request, 'projects/form.html', {'form': form, 'action': 'Oluştur'})


@login_required
def project_detail_view(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    check_project_access(request.user, project)

    tasks = project.tasks.select_related('assigned_worker', 'status').order_by('-created_at')
    members = project.members.select_related('user', 'role_in_project')

    return render(request, 'projects/detail.html', {
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

    return render(request, 'projects/form.html', {'form': form, 'action': 'Güncelle', 'project': project})


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

    return render(request, 'projects/confirm_delete.html', {'project': project})


@login_required
def project_toggle_view(request, pk: int):
    """Projeyi aktif ↔ pasif yapar."""
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
# GÖREV (TASK) — CRUD
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

    return render(request, 'tasks/form.html', {
        'form': form, 'project': project, 'action': 'Oluştur'
    })


@login_required
def task_detail_view(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    check_project_access(request.user, task.project)

    comments = task.comments.select_related('user').order_by('created_at')
    comment_form = CommentForm()

    return render(request, 'tasks/detail.html', {
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

    return render(request, 'tasks/form.html', {
        'form': form, 'project': task.project, 'action': 'Güncelle', 'task': task
    })


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

    return render(request, 'tasks/confirm_delete.html', {'task': task})


# -------------------------------------------------------
# YORUM (COMMENT)
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

    # Sadece yorumu yazan veya staff silebilir
    if comment.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        log_action(request.user, f"Yorum silindi (Görev: '{comment.task.task_name}')")
        comment.delete()
        messages.success(request, "Yorum silindi.")

    return redirect('task_detail', pk=task_pk)


# -------------------------------------------------------
# YÖNETİM PANELİ (Admin Only)
# -------------------------------------------------------

@login_required
@role_required(['Admin'])
def admin_dashboard_view(request):
    context = {
        'user_count': User.objects.count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'project_count': Project.objects.count(),
        'active_project_count': Project.objects.filter(is_active=True).count(),
        'task_count': Task.objects.count(),
        'recent_logs': ActionLog.objects.select_related('user').order_by('-timestamp')[:20],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@role_required(['Admin'])
def admin_user_list_view(request):
    users = User.objects.select_related('role', 'membership').order_by('username')
    return render(request, 'admin_panel/users.html', {'users': users})


@login_required
@role_required(['Admin'])
def admin_user_toggle_view(request, pk: int):
    """Kullanıcıyı aktif ↔ pasif yap."""
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
    return render(request, 'admin_panel/projects.html', {'projects': projects})


@login_required
@role_required(['Admin'])
def admin_log_view(request):
    logs = ActionLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'admin_panel/logs.html', {'logs': logs})