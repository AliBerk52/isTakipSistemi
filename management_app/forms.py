from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, Project, Task, Comment, TaskStatus


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password]
    )
    password_confirm = forms.CharField(
        label="Şifre (Tekrar)",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanımda.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        pw2 = cleaned_data.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label="Kullanıcı Adı", max_length=150)
    password = forms.CharField(label="Şifre", widget=forms.PasswordInput)
    remember_me = forms.BooleanField(label="Beni Hatırla", required=False)

    def clean_username(self):
        return self.cleaned_data.get('username', '').strip()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("Bitiş tarihi başlangıç tarihinden önce olamaz.")
        return cleaned_data


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_name', 'description', 'assigned_worker', 'status', 'status_mes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'status_mes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            #Sadece o projenin üyelerini göster
            member_ids = project.members.values_list('user_id', flat=True)
            self.fields['assigned_worker'].queryset = User.objects.filter(id__in=member_ids)
        self.fields['status'].queryset = TaskStatus.objects.all()
        self.fields['assigned_worker'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Yorumunuzu yazın...'}),
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="E-posta Adresi")


class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(
        label="Yeni Şifre",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password]
    )
    new_password_confirm = forms.CharField(
        label="Yeni Şifre (Tekrar)",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('new_password')
        pw2 = cleaned_data.get('new_password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return cleaned_data