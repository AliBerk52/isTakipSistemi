from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ================
# 1. YETKİLENDİRME
# ================

class Role(models.Model):
    role_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.role_name

class Department(models.Model):
    """Kullanıcıların bağlı olduğu departmanlar (Yazılım, Tasarım vb.)"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Membership(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_projects = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

class User(AbstractUser):
    base_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.is_superuser:
            return f"ADMIN: {self.username}"
        return f"USER: {self.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subLevel = models.CharField(max_length=50, blank=True, null=True) 
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# =================
# 2. PROJE YÖNETİMİ
# =================

class Project(models.Model):
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now) 
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.project_name

    @property
    def project_admin(self):
        """Project Manager rolündeki ilk üyeyi döner."""
        member = self.members.filter(
            role_in_project__role_name='Project Manager'
        ).select_related('user').first()
        return member.user if member else None

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role_in_project = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('project', 'user')

# ========================
# 3. GÖREVLER VE ETKİLEŞİM
# ========================

class TaskStatus(models.Model):
    status_name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return self.status_name

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.task_name

class Comment(models.Model):
    """Zorunlu Tablo: Görevlere yapılan yorumlar"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.task_name}"

# ======================
# 4. GÜVENLİK VE LOGLAMA
# ======================

class ActionLog(models.Model):
    """Nihai yönetim paneli için sistem hareketleri"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action}"

class ActivityLog(models.Model):
    """Genel aktivite kayıtları"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    createdAt = models.DateTimeField(default=timezone.now) 

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    createdAt = models.DateTimeField(default=timezone.now)