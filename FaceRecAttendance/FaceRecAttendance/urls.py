from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_login(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("dashboard")  # Redirect to Dashboard if already logged in

urlpatterns = [
    path("", redirect_to_login),
    path("admin/", admin.site.urls),
    path("auth/", include("auth_app.urls")),
    path("dashboard/", include("dashboard_app.urls")),
    path("courses/", include("course_app.urls")),
    path("attendance/", include("attendance_app.urls")),
]
