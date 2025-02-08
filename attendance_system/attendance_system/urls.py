from django.contrib import admin
from django.urls import path, include
from users.views import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='home'),  # Redirect '/' to dashboard
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
]
