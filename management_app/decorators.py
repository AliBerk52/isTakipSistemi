from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            #user giriş yapmamışsa veya rolü yeterli değilse 403 ver
            if not request.user.is_authenticated or request.user.role not in allowed_roles:
                raise PermissionDenied #yetkisiz giremen
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator