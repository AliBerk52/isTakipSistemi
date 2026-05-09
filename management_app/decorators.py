from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles:list):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            user_role_name = None
            if request.user.base_role:
                user_role_name = request.user.base_role.role_name

            if user_role_name not in allowed_roles:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator