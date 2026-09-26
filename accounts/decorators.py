from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if hasattr(request.user, 'profile') and request.user.profile.is_admin():
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard:index')
    return _wrapped_view
