from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def manager_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ('admin', 'manager'):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper
