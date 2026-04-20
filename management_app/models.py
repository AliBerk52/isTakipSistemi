from django.db import models
from django.contrib.auth.models import AbstractUser

# ==========================================
# 1. KULLANICI VE YETKİLENDİRME GRUBU (5 Tablo)
# ==========================================

class Membership(models.Model):
    """Üyelik paketlerini tanımlar (Free, Pro, Business vb.)"""
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_projects = models.PositiveIntegerField(default=1)
    max_users = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.name


class Role(models.Model):
    """Kullanıcı rollerini tutar (Admin, Project Manager, Worker)"""
    role_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.role_name


class Department(models.Model):
    """Kullanıcıların bağlı olduğu departmanlar (Yazılım, Tasarım vb.)"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Zorunlu Tablo: User
    Django'nun kendi User tablosunu genişletiyoruz.
    id, username, password, email, first_name (name), last_name (surname) otomatik gelir.
    """
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """Kullanıcının ekstra kişisel bilgilerini tutar."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subLevel = models.CharField(max_length=50, blank=True, null=True) # Belirttiğin özel alan
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ==========================================
# 2. PROJE YÖNETİMİ GRUBU (3 Tablo)
# ==========================================

class Project(models.Model):
    """Zorunlu Tablo: Project"""
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True) # openProject/closeProject için

    def __str__(self):
        return self.project_name


class ProjectMember(models.Model):
    """Hangi projede kimin, hangi rolle çalıştığını tutar (Many-to-Many ara tablosu)"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_projects')
    role_in_project = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True) # Projeye özel rol (örn: PM)

    class Meta:
        unique_together = ('project', 'user') # Bir kullanıcı bir projede sadece bir kez yer alabilir


class ProjectFile(models.Model):
    """Projeye yüklenen dosyalar/dokümanlar"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.project.project_name}"


# ==========================================
# 3. GÖREV VE ETKİLEŞİM GRUBU (4 Tablo)
# ==========================================

class TaskStatus(models.Model):
    """Görev durumları (Yapılacak, Devam Ediyor, Test, Tamamlandı)"""
    status_name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=7, default="#FFFFFF") # Frontend için hex kodu

    def __str__(self):
        return self.status_name


class Task(models.Model):
    """Zorunlu Tablo: Task"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True)
    status_mes = models.TextField(blank=True, null=True) # Belirttiğin özel mesaj alanı
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name


class Comment(models.Model):
    """Zorunlu Tablo: Comment (Görev altındaki yorumlar)"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.task_name}"


class ActivityLog(models.Model):
    """Sistemdeki hareketleri kaydetmek için (Loglama)"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action}"












#benim nihai yönetim panelim için lazım -loglar-
class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

#şifre sıfırlama tokenlerimiz
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)

#oturum yönetimi zaman aşımı için -yönetim paneli için lazm-
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    createdAt = models.DateTimeField(auto_now_add=True)