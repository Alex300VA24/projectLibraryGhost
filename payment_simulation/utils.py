import re
from django.conf import settings
from django.urls import reverse


def build_simulation_absolute_uri(request, view_name, **kwargs):
    path = reverse(view_name, kwargs=kwargs)
    host = request.get_host()
    ip_destino = getattr(settings, 'IP_DESTINO', '')

    if ip_destino:
        host = re.sub(r'localhost|127\.0\.0\.1', ip_destino, host)

    scheme = 'https' if request.is_secure() else 'http'
    return f'{scheme}://{host}{path}'
