from management_app.models import User, Role

# Role
admin_role, _ = Role.objects.get_or_create(role_name='Admin')
worker_role, _ = Role.objects.get_or_create(role_name='Worker')

# Admin user
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123456',
    base_role=admin_role
)
print(f"✓ Admin oluşturuldu: {admin_user.username}")

# 10 Worker user
for i in range(1, 11):
    worker = User.objects.create_user(
        username=f'worker{i}',
        email=f'worker{i}@example.com',
        password='worker123456',
        base_role=worker_role
    )
    print(f" Worker{i} oluşturuldu: {worker.username}")

print("\n Toplam 1 admin + 10 worker başarıyla eklendi")
