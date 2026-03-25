from django.db import models
from django.contrib.auth.models import AbstractUser

#abonelik(junior,medior,senior olcak)
class SubscriptionLevel(models.Model):
    name = models.CharField(max_length=50) 
    def __str__(self):
        return self.name

#roller(hazaldan not: djangonun abstractuser sınıfı id name surname password alanlarını oto dahil ediyor yine de düzenlemek istersen bu kısmı değiştirmen gerekebilir)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('PROJECT_MANAGER', 'Project Manager'),
        ('WORKER', 'Worker'),
        ('CLIENT', 'Client'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    subLevel = models.ForeignKey(SubscriptionLevel, on_delete=models.SET_NULL, null=True, blank=True)

#eksik devamı sende dosya içerikleri kısmında kesinlikle olması gerekenleri belirttim zaten
class Project(models.Model):
    projectName = models.CharField(max_length=200)
    startDate = models.DateField()
    endDate = models.DateField()












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