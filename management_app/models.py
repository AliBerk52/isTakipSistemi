from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone # Dünya zamanı (UTC/Sistem saati) için bu şart

# ==========================================
# 1. YETKİLENDİRME VE ROL YAPISI
# ==========================================

class Role(models.Model):
    role_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.role_name

class Membership(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_projects = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

class User(AbstractUser):
    base_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)

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

# ==========================================
# 2. PROJE YÖNETİMİ (Takvim Zamanı)
# ==========================================

class Project(models.Model):
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    # Form hatasını önlemek için default=timezone.now kullanıyoruz
    # Bu sayede hem 'dünya zamanı' varsayılan gelir hem de formda düzenlenebilir
    start_date = models.DateField(default=timezone.now) 
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.project_name

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role_in_project = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('project', 'user')

# ==========================================
# 3. GÖREVLER VE ETKİLEŞİM
# ==========================================

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
    created_at = models.DateTimeField(default=timezone.now) # Sistem zamanı

# ==========================================
# 4. GÜVENLİK VE ŞİFRE (Dünya Zamanı - Precise Time)
# ==========================================

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    # Şifre sıfırlama için saniyesi saniyesine dünya zamanı gerekir
    createdAt = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"Reset Token for {self.user.username}"

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    createdAt = models.DateTimeField(default=timezone.now)