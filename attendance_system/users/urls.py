# users/urls.py
from django.urls import path
from . import views
from .views import dashboard_view, manage_users_view, create_user_view, edit_user_view, delete_user_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    path('manage-users/', manage_users_view, name='manage_users'),
    path('create-user/', create_user_view, name='create_user'),
    path('edit-user/<int:user_id>/', edit_user_view, name='edit_user'),
    path('delete-user/<int:user_id>/', delete_user_view, name='delete_user'),
]
