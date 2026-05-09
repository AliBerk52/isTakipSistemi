from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Membership, Role, Department, User, UserProfile,
    Project, ProjectMember,
    TaskStatus, Task, Comment, ActivityLog,
    ActionLog, PasswordResetToken, UserSession
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'membership', 'is_active']
    list_filter = ['role', 'membership', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Proje Sistemi', {'fields': ('role', 'membership')}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['project_name']
    actions = ['activate_projects', 'deactivate_projects']

    @admin.action(description="Seçili projeleri aktif yap")
    def activate_projects(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Seçili projeleri pasif yap")
    def deactivate_projects(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'project', 'assigned_worker', 'status', 'created_at']
    list_filter = ['status', 'project']
    search_fields = ['task_name']
    raw_id_fields = ['assigned_worker']


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'action']
    readonly_fields = ['user', 'action', 'timestamp']

    def has_add_permission(self, request):
        return False  # Log'lar manuel eklenemez

    def has_change_permission(self, request, obj=None):
        return False  # Log'lar değiştirilemez


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'created_at']
    search_fields = ['content', 'user__username']


# Basit kayıtlar
admin.site.register(Membership)
admin.site.register(Role)
admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(ProjectMember)
admin.site.register(TaskStatus)
admin.site.register(ActivityLog)
admin.site.register(PasswordResetToken)
admin.site.register(UserSession)
