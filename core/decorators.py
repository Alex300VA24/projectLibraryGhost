from functools import wraps

from django.http import HttpResponseForbidden


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_staff or
                (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.name in ('admin', 'employee'))):
            return HttpResponseForbidden('No tienes permiso para acceder a esta pagina.')
        return view_func(request, *args, **kwargs)
    return wrapper
