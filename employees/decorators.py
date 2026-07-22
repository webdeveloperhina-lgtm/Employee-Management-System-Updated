from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def hr_required(view_func):
    """Allow authenticated HR/admin accounts, not linked employee accounts."""

    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if hasattr(request.user, "employee_profile"):
            return redirect("employee_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapped

