# users/urls.py
from django.urls import path
from . import views
from .views import dashboard_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
