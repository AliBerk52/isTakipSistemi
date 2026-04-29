from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings

# settings.py'de SESSION_TIMEOUT_SECONDS tanımlanmamışsa 30 dakika default
SESSION_TIMEOUT = getattr(settings, 'SESSION_TIMEOUT_SECONDS', 1800)


class SessionTimeoutMiddleware:
    """
    Son aktiviteden itibaren SESSION_TIMEOUT saniye geçmişse
    kullanıcıyı otomatik olarak oturumdan çıkarır.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity_str = request.session.get('last_activity')

            if last_activity_str:
                last_activity = parse_datetime(last_activity_str)
                if last_activity:
                    elapsed = (timezone.now() - last_activity).total_seconds()
                    if elapsed > SESSION_TIMEOUT:
                        logout(request)
                        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            # Her requestte son aktivite zamanını güncelle
            request.session['last_activity'] = timezone.now().isoformat()
            request.session.modified = True

        return self.get_response(request)
