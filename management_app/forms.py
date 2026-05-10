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
    remember_me = forms.BooleanField(required=False)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].required = False  # template'de yok, modelde default var
        self.fields['end_date'].required = False

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # 1. views.py'den gelen 'project' argümanını kwargs'tan çıkar ve yakala
        project = kwargs.pop('project', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        # 2. Eğer proje verisi geldiyse dropdown listesini filtrele
        if project:
            # Sadece projeye atanmış aktif kullanıcıları listele
            self.fields['assigned_worker'].queryset = User.objects.filter(
                project_assignments__project=project,
                is_active=True
            ).distinct()

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