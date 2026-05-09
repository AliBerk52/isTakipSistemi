from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Project, Task, Comment

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_name', 'description', 'assigned_worker', 'status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
