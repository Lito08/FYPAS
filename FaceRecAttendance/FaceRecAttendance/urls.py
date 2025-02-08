from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard_app.urls")),
    path("auth/", include("auth_app.urls")),
    path("courses/", include("course_app.urls")),
    path("attendance/", include("attendance_app.urls")),
]
