from django.shortcuts import redirect
from django.contrib import messages


def LogoutCheckMiddleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return get_response(request)
    return middleware


def status_check_middleware(get_response):
    def middleware(request):
        if not request.user.is_staff and request.user.status != "Student":
            messages.error(request, "Can't access the requested page because you are a driver!")
            return redirect("driver_dashboard")
        return get_response(request)
    return middleware


def driver_check_middleware(get_response):
    def middleware(request):
        if request.user.status != "Driver":
            messages.error(request, "Can't access the requested page because you are not a driver!")
            return redirect("dashboard")
        return get_response(request)
    return middleware