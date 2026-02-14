from django.shortcuts import redirect
from .models import UserProfile

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return redirect('login')

            if profile.role not in allowed_roles:
                return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
